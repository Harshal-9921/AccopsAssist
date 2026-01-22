📘 Accops AI Documentation Assistant (RAG-based)
📌 Project Overview

This project is an AI-powered documentation assistant built for Accops products (HyWorks & HySecure).
It uses Retrieval-Augmented Generation (RAG) to answer user queries accurately based on official Accops documentation.

The system also includes an Admin module to track usage analytics such as:

Total queries

Product-wise usage

Top asked questions

CSV-based audit logs (IP + timestamp)

🧱 Architecture Overview
Frontend (Chat Widget)
        |
        |  POST /ask
        v
FastAPI Backend
        |
        |-- RAG Engine (FAISS + HuggingFace Embeddings)
        |-- OpenAI LLM (GPT-4o-mini)
        |-- Usage Logger (CSV)
        |
        |-- /admin APIs (secured)

🛠️ Tech Stack Used
Backend

Python 3.10+

FastAPI

LangChain

FAISS (Vector Database)

HuggingFace Sentence Transformers

OpenAI GPT-4o-mini

Frontend

HTML, CSS, JavaScript

Fetch API

Markdown rendering (marked.js)

Storage

CSV-based logging (for analytics)

FAISS local vector store

📂 Project Structure
rag-chat-widget/
│
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── rag.py                # Core RAG logic
│   ├── ingest.py             # Document ingestion
│   ├── product_definitions.py
│   ├── data/
│   │   └── usage_logs.csv    # Auto-generated logs
│
├── admin/
│   ├── admin_api.py          # Admin endpoints
│   ├── auth.py               # Admin auth
│   └── usage_logger.py       # CSV logger
│
├── analytics/
│   └── reader.py             # Reads CSV for stats
│
├── frontend/
│   ├── index.html            # Chat widget
│   └── admin.html            # Admin dashboard UI
│
├── vector_store/
│   └── accops_docs/          # FAISS index (generated)
│
├── requirements.txt
└── README.md

⚙️ Setup Instructions (Step-by-Step)
1️⃣ Clone Repository
git clone <repo-url>
cd rag-chat-widget

2️⃣ Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Environment Variables

Create .env (optional but recommended):

OPENAI_API_KEY=your_openai_key
ADMIN_SECRET=admin123

5️⃣ Ingest Documentation (ONE-TIME STEP)

This builds the vector database from Accops docs.

python backend/ingest.py


✅ This will create:

vector_store/accops_docs

6️⃣ Run Backend Server
uvicorn backend.main:app --reload


Expected output:

Uvicorn running on http://127.0.0.1:8000
Application startup complete.

💬 Chat Usage

Open:

frontend/index.html


Example test questions:

What is HyWorks?

Integration with Active Directory steps

HySecure gateway configuration

What ports are required for HyWorks?

📊 Admin Features
Admin APIs (Protected)
Endpoint	Description
/admin/usage-summary	Query count + product split
/admin/top-questions	Most asked queries
/admin/download-csv	Download usage logs

Authorization Header

Authorization: Bearer admin123

📁 Usage Logs

Stored at:

backend/data/usage_logs.csv


Format:

timestamp,question,product,ip_address


Example:

2025-12-31 13:34:54,what is HyWorks?,HyWorks,127.0.0.1

🔐 Security Notes

Admin APIs are token-protected

No user PII stored

Only IP + question logged for analytics

LLM usage is rate-limited via token control

🚀 Deployment Readiness

The project is ready for:

Internal testing

Security review

DOCS environment deployment (after infra approval)


📌 Notes for Team

Backend is fully functional

RAG answers are sourced strictly from Accops docs

Admin UI wiring is in progress

Logging and analytics are production-ready
