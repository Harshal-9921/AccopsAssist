🚀 Accops AI Assistant (RAG-based Documentation Chat)
An AI-powered documentation assistant for Accops products (HyWorks & HySecure) using FastAPI + RAG (Retrieval-Augmented Generation).
It provides a user chat console and a secure admin dashboard for analytics and usage tracking.
________________________________________
📌 Features
✅ User Features
•	Floating chat widget (web-based)
•	Answers questions from Accops documentation
•	Supports product-specific queries:
o	HyWorks
o	HySecure
•	Clean, Markdown-formatted responses
🔐 Admin Features
•	Secure Admin Dashboard
•	Tracks:
o	Total queries
o	Product-wise usage
o	Top asked questions
o	User IP addresses
•	Download usage report as CSV
•	Admin-only API access
________________________________________
🧱 Tech Stack
Layer	Technology
Frontend	HTML, CSS, JavaScript
Backend	FastAPI (Python)
AI	LangChain + OpenAI
Embeddings	HuggingFace (MiniLM)
Vector DB	FAISS
Analytics	CSV-based logging
Auth	Admin Secret (Header-based)
________________________________________
📁 Project Structure
rag-chat-widget/
│
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── rag.py                # RAG logic
│   ├── product_definitions.py
│   ├── vector_store/
│   └── data/
│       └── usage_logs.csv
│
├── admin/
│   ├── admin_api.py          # Admin routes
│   ├── auth.py               # Admin authentication
│   └── usage_logger.py       # CSV logging
│
├── analytics/
│   └── reader.py             # CSV analytics
│
├── frontend/
│   ├── index.html            # User chat UI
│   └── admin.html            # Admin dashboard
│
├── ingest.py                 # Document ingestion
├── requirements.txt
└── README.md
________________________________________
⚙️ Setup Instructions
1️ Clone Repository
git clone https://github.com/Harshal-9921/AccopsAssist.git
cd AccopsAssist
________________________________________
2️ Create Virtual Environment
python -m venv .venv
Activate:
Windows
.venv\Scripts\activate
Linux / Mac
source .venv/bin/activate
________________________________________
3️ Install Dependencies
pip install -r requirements.txt
________________________________________
4️ Set Environment Variables
Create a .env file :
OPENAI_API_KEY=
ADMIN_SECRET=
________________________________________
5️ Ingest Documentation (One-Time)
This creates the vector database.
python ingest.py
Make sure this folder exists after running:
backend/vector_store/accops_docs
________________________________________
6️ Run Backend Server
uvicorn backend.main:app --reload
Server runs at:
http://localhost:8000
________________________________________
💬 User Console (Chat)
Access
•	Open frontend/index.html in browser
•	Click chat icon (bottom-right)
Test Questions
•	What is HyWorks?
•	Integration with Active Directory steps
•	HySecure gateway unreachable error
•	What ports are required for HyWorks?
•	How to reset admin password?
________________________________________
📊 Admin Dashboard
Access
•	Open frontend/admin.html
•	Login using admin key (default: admin123)
Admin APIs
GET /admin/usage-summary
GET /admin/top-questions
GET /admin/download-csv
CSV Log Location
backend/data/usage_logs.csv
Sample entry:
2025-12-31 13:33:14, what is HyWorks?, HyWorks, 127.0.0.1
________________________________________
🔐 Security Notes
•	Admin APIs are protected using Bearer Token
•	Only authorized users can access analytics
•	Normal users cannot view admin data
 Testing Checklist
•	 Chat answers correctly
•	 CSV logs are updated
•	 Admin dashboard loads data
•	 CSV download works
•	 Unauthorized admin access blocked.
