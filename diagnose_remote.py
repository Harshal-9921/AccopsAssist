import paramiko
import getpass
import sys

# Configuration
REMOTE_HOST = "172.27.11.194"
REMOTE_USER = "k8s"
REMOTE_DIR = "rag-chat-widget"

def diagnose(password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔌 Connecting to {REMOTE_HOST}...")
        client.connect(REMOTE_HOST, username=REMOTE_USER, password=password, timeout=10)
        print("✅ Connected.")
        
        commands = [
            ("🔍 Process Status", "ps aux | grep uvicorn"),
            ("🔍 Listening Ports", "netstat -tulnp | grep 8000 || ss -tulnp | grep 8000"),
            ("🔥 Firewall Status (UFW)", "sudo ufw status verbose"),
            ("📝 Application Log (Last 20 lines)", f"tail -n 20 {REMOTE_DIR}/app.log")
        ]
        
        for title, cmd in commands:
            print(f"\n--- {title} ---")
            # sudo might prompt for password, so we use -S and write to stdin if needed, 
            # but for 'ufw status' usually one needs sudo. 
            # Simplified approach: try running. If it needs sudo, we might pass password.
            if "sudo" in cmd:
                 stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
                 stdin.write(password + "\n")
                 stdin.flush()
            else:
                 stdin, stdout, stderr = client.exec_command(cmd)
            
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            
            if out: print(out)
            if err: print(f"Error: {err}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
    else:
        pwd = getpass.getpass(prompt=f"Enter SSH password for {REMOTE_USER}@{REMOTE_HOST}: ")
    diagnose(pwd)
