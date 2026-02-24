import os
import zipfile
import paramiko
import getpass
import time
import sys

# Configuration
REMOTE_HOST = "172.27.11.194"
REMOTE_USER = "k8s"
REMOTE_DIR = "rag-chat-widget"
ZIP_NAME = "deploy_package.zip"

FILES_TO_ZIP = [
    "backend",
    "frontend",
    "admin",
    "vector_store",
    "requirements.txt",
    ".env"
]

def create_zip():
    print(f"📦 Creating {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in FILES_TO_ZIP:
            if os.path.isfile(item):
                zipf.write(item)
            elif os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        # Skip __pycache__
                        if "__pycache__" in root:
                            continue
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
    print("✅ Zip created.")

def deploy(password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔌 Connecting to {REMOTE_USER}@{REMOTE_HOST}...")
        ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=password, timeout=10)
        print("✅ Connected via SSH.")
        
        # SFTP Upload
        sftp = ssh.open_sftp()
        try:
            print(f"📂 Creating remote directory: {REMOTE_DIR}...")
            try:
                sftp.mkdir(REMOTE_DIR)
            except IOError:
                pass # Directory likely exists
            
            print(f"⬆️ Uploading {ZIP_NAME}...")
            sftp.put(ZIP_NAME, f"{REMOTE_DIR}/{ZIP_NAME}")
            print("✅ Upload complete.")
        finally:
            sftp.close()
        
        # Remote Commands
        commands = [
            # Extract using python to avoid 'unzip' dependency
            f"cd {REMOTE_DIR} && python3 -c \"import zipfile; [zipfile.ZipFile('{ZIP_NAME}').extractall() for _ in [0]]\"",
            f"cd {REMOTE_DIR} && python3 -m venv .venv",
            f"cd {REMOTE_DIR} && source .venv/bin/activate && pip install -r requirements.txt",
            # Kill existing uvicorn process
            "sudo pkill -f 'uvicorn backend.main:app' || true",
            # Start new process on PORT 80 (Requires sudo)
            # We use string formatting to inject the password for sudo -S
            # Note: This is a bit hacky but works for simple deployment scripts.
            f"echo '{password}' | sudo -S nohup {REMOTE_DIR}/.venv/bin/uvicorn backend.main:app --app-dir {REMOTE_DIR} --host 0.0.0.0 --port 80 > {REMOTE_DIR}/app.log 2>&1 &"
        ]
        
        for cmd in commands:
            print(f"🏃 Running remote command: {cmd[:50]}...") # Verify command (hide password in logs if possible, but hard here due to strict slicing)
            
            # Special handling for sudo with echo pipe
            stdin, stdout, stderr = ssh.exec_command(cmd)
            
            # For long running commands like pip install, stream output
            if "pip install" in cmd:
                for line in iter(stdout.readline, ""):
                    print(line, end="")
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0 and "pkill" not in cmd:
                print(f"❌ Command failed: {stderr.read().decode()}")
                return
            
        print("\n✅ Application deployed and started!")
        print(f"🌐 Access at: http://{REMOTE_HOST}/")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
    finally:
        ssh.close()
        # Cleanup
        if os.path.exists(ZIP_NAME):
            os.remove(ZIP_NAME)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
    else:
        pwd = getpass.getpass(prompt=f"Enter SSH password for {REMOTE_USER}@{REMOTE_HOST}: ")
    
    create_zip()
    deploy(pwd)
