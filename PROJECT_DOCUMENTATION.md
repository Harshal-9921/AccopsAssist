# 📚 Accops RAG Chat Widget - Complete Project Documentation

**Project Name:** Accops AI Documentation Assistant  
**Type:** RAG-based Chatbot with Admin Dashboard  
**Tech Stack:** Python (FastAPI), JavaScript, FAISS, OpenAI GPT-4o-mini, LangChain  
**Purpose:** Intelligent documentation assistant for Accops HyWorks & HySecure products

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Folder Structure](#folder-structure)
4. [Backend Components](#backend-components)
5. [Frontend Components](#frontend-components)
6. [Admin Module](#admin-module)
7. [Analytics Module](#analytics-module)
8. [Data Storage](#data-storage)
9. [API Endpoints](#api-endpoints)
10. [How It Works](#how-it-works)
11. [Setup & Installation](#setup--installation)
12. [Configuration Files](#configuration-files)

---

## 🎯 Project Overview

This is a **Retrieval-Augmented Generation (RAG)** chatbot that answers questions about Accops products by:
1. Searching through indexed documentation (vector database)
2. Finding relevant content chunks
3. Using AI (GPT-4o-mini) to generate accurate, context-aware answers
4. Tracking usage analytics and user feedback

**Key Features:**
- ✅ Product-specific answer retrieval (HySecure vs HyWorks)
- ✅ Real-time thinking indicator ("🤔 Thinking...")
- ✅ User feedback collection (👍 👎)
- ✅ Admin dashboard with analytics
- ✅ Usage logging with IP tracking
- ✅ Confidence-based clarification requests

---

## 🏗️ Architecture & Data Flow

```
┌─────────────────┐
│   USER BROWSER  │
│  (Chat Widget)  │
└────────┬────────┘
         │
         │ HTTP POST /ask
         ▼
┌─────────────────────────────────────────┐
│          FASTAPI BACKEND                │
│  (backend/main.py - Port 8000)          │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  1. Receive Question             │  │
│  │  2. Product Detection            │  │
│  │  3. RAG Processing               │  │
│  │     ├─ Vector Search (FAISS)     │  │
│  │     ├─ Product Filtering         │  │
│  │     ├─ LLM Answer Generation     │  │
│  │     └─ Confidence Assessment     │  │
│  │  4. Log Usage (CSV)              │  │
│  │  5. Return Answer + response_id  │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         │ Response with answer
         ▼
┌─────────────────┐
│   USER SEES:    │
│  - Answer       │
│  - Sources      │
│  - Feedback 👍👎│
└─────────────────┘
         │
         │ POST /feedback (optional)
         ▼
┌─────────────────┐
│  Update CSV     │
│  with feedback  │
└─────────────────┘

         ADMIN SIDE:
┌─────────────────┐
│  Admin Login    │
│  (admin123)     │
└────────┬────────┘
         │
         │ GET /admin/usage-summary
         │ GET /admin/recent-logs
         ▼
┌─────────────────┐
│  Dashboard UI   │
│  - Total Queries│
│  - Feedback     │
│  - Analytics    │
└─────────────────┘
```

---

## 📂 Folder Structure

```
d:\C BACKUP\rag-chat-widget/
│
├── 📁 backend/                    # ⭐ CORE BACKEND LOGIC
│   ├── __init__.py               # Python package marker
│   ├── main.py                   # 🚀 FastAPI app entry point (PORT 8000)
│   ├── rag.py                    # 🧠 RAG engine (vector search + LLM)
│   ├── ingest.py                 # 📥 Document scraper & vectorizer
│   ├── product_definitions.py    # 📖 Product info (HyWorks, HySecure)
│   └── vector_store/             # (Optional: duplicate vector store)
│
├── 📁 admin/                      # 🔒 ADMIN MODULE
│   ├── __init__.py
│   ├── admin_api.py              # 📊 Admin REST API endpoints
│   ├── admin.html                # 🖥️ Admin dashboard UI (browser)
│   ├── auth.py                   # 🔐 Admin authentication (Bearer token)
│   └── usage_logger.py           # 📝 CSV logging utility
│
├── 📁 analytics/                  # 📈 ANALYTICS MODULE
│   ├── __init__.py
│   ├── logger.py                 # (Placeholder/unused)
│   └── reader.py                 # 📖 CSV data reader (stats, top questions)
│
├── 📁 frontend/                   # 💬 FRONTEND (USER-FACING)
│   └── index.html                # 🖼️ Chat widget UI (main user interface)
│
├── 📁 data/                       # 💾 DATA STORAGE
│   └── usage_logs.csv            # 📄 All queries + feedback (auto-generated)
│
├── 📁 vector_store/               # 🗄️ VECTOR DATABASE
│   └── accops_docs/
│       ├── index.faiss           # 🔢 FAISS vector index
│       └── index.pkl             # 🗂️ Metadata (sources, URLs)
│
├── 📁 docs/                       # 📚 Documentation (optional)
│
├── 📁 .venv/                      # 🐍 Python virtual environment
├── 📁 .vscode/                    # ⚙️ VS Code settings
│
├── .env                          # 🔑 Environment variables (OPENAI_API_KEY)
├── .gitignore                    # 🚫 Git ignore rules
├── requirements.txt              # 📦 Python dependencies
├── README.md                     # 📘 Project readme
└── PROJECT_DOCUMENTATION.md      # 📚 This file!
```

---

## 🔧 Backend Components

### 📍 Location: `backend/`

### 1. **`main.py`** - FastAPI Application Entry Point

**What it does:**
- Starts the FastAPI web server on port 8000
- Defines HTTP endpoints (`/ask`, `/feedback`, `/admin/*`)
- Handles CORS (allows frontend to communicate)
- Logs each query to CSV

**Key Endpoints:**
```python
POST /ask              # User asks a question
POST /feedback         # User submits 👍/👎 feedback
GET  /admin/*          # Admin dashboard APIs
```

**Code Flow:**
```
User Question → /ask endpoint
  ↓
1. Extract question from request
2. Call get_rag_answer() from rag.py
3. Detect product (HyWorks/HySecure)
4. Log to CSV (question, product, IP, timestamp)
5. Return { answer, response_id }
```

---

### 2. **`rag.py`** - RAG Engine (Brain of the System)

**What it does:**
- Performs **Retrieval-Augmented Generation**
- Searches vector database for relevant documentation chunks
- Filters by product (HySecure vs HyWorks)
- Generates answer using OpenAI GPT-4o-mini
- Assesses answer confidence
- Asks for clarification if uncertain

**Key Functions:**

#### `get_embeddings()`
- Initializes HuggingFace sentence embeddings model
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Converts text to 384-dimensional vectors

#### `get_db()`
- Loads FAISS vector database
- Path: `vector_store/accops_docs/`

#### `get_rag_answer(question: str) → str`
**Main RAG logic:**
```python
1. Detect product from question (hysecure/hyworks)
2. Retrieve 8 similar document chunks from vector DB
3. Filter chunks by product metadata
4. Build context (max 800 chars per chunk)
5. Send to LLM with prompt
6. Get answer
7. Assess confidence
8. Add clarification request if low confidence (<0.6)
9. Append source links
10. Return formatted answer
```

**Product-Aware Filtering:**
```python
# If question contains "hysecure"
target_product = "hysecure"

# Filter docs by metadata
filtered_docs = [doc for doc in all_docs 
                 if doc.metadata.get("module") == "HySecure"]
```

**Confidence Assessment:**
Detects phrases like:
- "I don't have"
- "not found"
- "unclear"
- "unable to"

If confidence < 0.6, adds:
```
📝 To help you better, could you provide more details? For example:
- What version of the product are you using?
- What specific issue or feature are you asking about?
- Are you looking for configuration, troubleshooting, or usage information?
```

---

### 3. **`ingest.py`** - Document Scraper & Vector Database Builder

**What it does:**
- Crawls Accops documentation websites
- Scrapes HTML content
- Splits into chunks (1200 characters)
- Converts to embeddings
- Stores in FAISS vector database

**Configuration:**
```python
SEED_URLS = [
    "https://docs.accops.com/HyWorks34sp2/index.html",
    "https://docs.accops.com/hysecure_7_2/index.html"
]

CHUNK_SIZE = 1200      # Characters per chunk
CHUNK_OVERLAP = 150    # Overlap between chunks
OUTPUT_DIR = "vector_store/accops_docs"
```

**How to run:**
```bash
python backend/ingest.py
```

**Output:**
```
🔍 Crawling links from: https://docs.accops.com/hysecure_7_2/index.html
📄 Scraping: https://docs.accops.com/hysecure_7_2/management.html
✅ Discovered 150 documentation pages
✅ Created 3,278 document chunks
🎉 Vector database created successfully!
```

**Each chunk includes metadata:**
```python
{
    "source": "https://docs.accops.com/hysecure_7_2/roles.html",
    "module": "HySecure"
}
```

---

### 4. **`product_definitions.py`** - Product Information

**What it does:**
- Stores basic product definitions
- Used for fallback answers (currently not used in RAG flow)

```python
PRODUCT_DEFINITIONS = {
    "hyworks": {
        "answer": "HyWorks is Accops' Digital Workspace platform...",
        "source": "https://docs.accops.com/HyWorks34sp2/..."
    },
    "hysecure": {
        "answer": "HySecure is Accops' Zero Trust Secure Access gateway...",
        "source": "https://docs.accops.com/hysecure_7_2/index.html"
    }
}
```

---

## 💬 Frontend Components

### 📍 Location: `frontend/`

### **`index.html`** - Chat Widget UI

**What it does:**
- Provides chat interface for users
- Sends questions to backend
- Displays answers with markdown formatting
- Shows "🤔 Thinking..." while waiting
- Collects user feedback (👍 👎)
- Auto-scrolls to show answer start (not sources)

**Key Features:**

#### 1. **Chat Launcher**
- Floating orange button (bottom-right)
- Opens/closes chat window on click

#### 2. **Chat Window**
- 350px × 500px dialog
- User messages: Orange bubbles (right)
- AI messages: Gray bubbles (left)

#### 3. **Thinking Indicator**
```html
<div class="typing-indicator">
    <span class="typing-text">🤔 Thinking</span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
</div>
```

#### 4. **Feedback Buttons**
```html
<button onclick="sendFeedback('id123', 'positive')">👍</button>
<button onclick="sendFeedback('id123', 'negative')">👎</button>
```

**JavaScript Flow:**
```javascript
async function sendMessage() {
    1. Get user question
    2. Display user message
    3. Show "🤔 Thinking..." indicator
    4. POST /ask to backend
    5. Hide thinking indicator
    6. Parse markdown answer
    7. Display AI message
    8. Add feedback buttons
    9. Scroll to show start of answer
}
```

**Smart Scrolling:**
- User messages → Scroll to bottom
- AI messages → Scroll to **start of message** (not sources)
```javascript
if (sender === "ai") {
    div.scrollIntoView({ behavior: "smooth", block: "start" });
}
```

---

## 🔒 Admin Module

### 📍 Location: `admin/`

### 1. **`admin_api.py`** - Admin REST API

**Endpoints:**

#### `GET /admin/usage-summary`
Returns total queries and breakdown by product.
```json
{
  "total_queries": 124,
  "by_product": {
    "HyWorks": 80,
    "HySecure": 44
  }
}
```

#### `GET /admin/recent-logs?limit=10`
Returns recent queries from CSV.
```json
{
  "recent_logs": [
    {
      "datetime": "2026-01-25 10:45:00",
      "question": "What is HySecure?",
      "product": "HySecure",
      "ip": "192.168.1.100",
      "feedback": "positive"
    }
  ]
}
```

#### `GET /admin/top-questions`
Returns most frequently asked questions.

#### `GET /admin/download-csv`
Downloads the full usage logs CSV file.

---

### 2. **`auth.py`** - Authentication

**Security:**
- Uses Bearer token authentication
- Admin key: `admin123` (hardcoded for demo)
- All `/admin/*` endpoints require valid token

**Usage:**
```bash
curl -H "Authorization: Bearer admin123" \
     http://localhost:8000/admin/usage-summary
```

**Production Note:** Replace with proper authentication (JWT, OAuth, etc.)

---

### 3. **`admin.html`** - Admin Dashboard UI

**What it does:**
- Login screen (requires admin key)
- Stats cards (total, by product)
- Recent queries table
- Feedback analytics
- CSV download button

**Features:**

#### Login Overlay
```html
<input type="password" id="adminKey" placeholder="Enter key..." />
<!-- Admin key: admin123 -->
```

#### Stats Cards
```
┌─────────────────┐  ┌─────────────────┐
│ Total Queries   │  │ HyWorks Queries │
│      124        │  │       80        │
└─────────────────┘  └─────────────────┘
```

#### Recent Queries Table
```
Date & Time        | User Query           | Product  | IP         | Feedback
2026-01-25 10:45  | What is HySecure?    | HySecure | 127.0.0.1 | 👍 Helpful
2026-01-25 10:42  | HyWorks setup?       | HyWorks  | 127.0.0.1 | No Feedback yet
```

**Smart Display:**
- Shows oldest entries first (reversed order)
- Feedback icons: 👍 Helpful / 👎 Not Helpful / No Feedback yet

---

### 4. **`usage_logger.py`** - CSV Logger

**What it does:**
- Writes query logs to `data/usage_logs.csv`
- Ensures CSV schema compatibility
- Generates unique `response_id` for each query
- Updates feedback when user clicks 👍/👎

**Functions:**

#### `ensure_schema()`
Creates/migrates CSV to correct format:
```csv
Date and Time,User Query,Product,IP Address,feedback,response_id
```

#### `log_usage(question, product, ip) → response_id`
Logs a new query:
```python
response_id = "20260125104530a1b2c3"  # timestamp + random hex
```

#### `log_feedback(response_id, feedback)`
Updates feedback for a specific response:
```python
# Find row with matching response_id
# Update feedback column to "positive" or "negative"
```

---

## 📈 Analytics Module

### 📍 Location: `analytics/`

### **`reader.py`** - CSV Data Reader

**What it does:**
- Reads `data/usage_logs.csv`
- Calculates statistics
- Supports multiple CSV header formats (legacy compatibility)

**Functions:**

#### `usage_summary()`
```python
{
    "total_queries": 124,
    "by_product": {"HyWorks": 80, "HySecure": 44}
}
```

#### `top_questions(limit=5)`
```python
[
    {"question": "How to install HySecure?", "product": "HySecure", "count": 12},
    {"question": "HyWorks prerequisites?", "product": "HyWorks", "count": 8}
]
```

#### `recent_logs(limit=10)`
Returns last N entries with all columns.

**Header Flexibility:**
Supports various column names:
- `"Date and Time"` or `"datetime"` or `"Date"`
- `"User Query"` or `"question"`
- `"Product"` or `"product"`
- `"IP Address"` or `"ip"`

---

## 💾 Data Storage

### 📍 Location: `data/`

### **`usage_logs.csv`** - Query & Feedback Log

**Format:**
```csv
Date and Time,User Query,Product,IP Address,feedback,response_id
2026-01-25 10:45:30,What is HySecure?,HySecure,127.0.0.1,positive,20260125104530abc123
2026-01-25 10:42:15,HyWorks setup?,HyWorks,192.168.1.5,,20260125104215def456
```

**Columns:**
- `Date and Time`: Timestamp (YYYY-MM-DD HH:MM:SS)
- `User Query`: User's question
- `Product`: HyWorks or HySecure
- `IP Address`: User IP (from request.client.host)
- `feedback`: "positive", "negative", or empty
- `response_id`: Unique ID (timestamp + random hex)

**Auto-generated:**
- Created automatically when first query is logged
- Schema migration happens automatically

---

### 📍 Location: `vector_store/accops_docs/`

### **FAISS Vector Database**

**Files:**
- `index.faiss`: Binary vector index (3,278 document chunks)
- `index.pkl`: Pickle file with metadata

**What's stored:**
Each chunk:
```python
{
    "page_content": "HySecure Management Roles and Privileges allow...",
    "metadata": {
        "source": "https://docs.accops.com/hysecure_7_2/roles.html",
        "module": "HySecure"
    }
}
```

**Chunk Size:**
- 1200 characters per chunk
- 150 character overlap
- Total: 3,278 chunks from ~150 documentation pages

---

## 🔌 API Endpoints

### Public Endpoints (No Auth Required)

#### `POST /ask`
**Request:**
```json
{
  "question": "What is HySecure Management Roles?"
}
```

**Response:**
```json
{
  "answer": "**HySecure Management Roles** allow administrators to...\n\n🔗 **Source(s):**\n- https://docs.accops.com/hysecure_7_2/roles.html",
  "response_id": "20260125104530abc123"
}
```

#### `POST /feedback`
**Request:**
```json
{
  "response_id": "20260125104530abc123",
  "feedback": "positive"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

---

### Admin Endpoints (Require `Authorization: Bearer admin123`)

#### `GET /admin/usage-summary`
```json
{
  "total_queries": 124,
  "by_product": {
    "HyWorks": 80,
    "HySecure": 44
  }
}
```

#### `GET /admin/recent-logs?limit=10`
```json
{
  "recent_logs": [
    {
      "datetime": "2026-01-25 10:45:30",
      "question": "What is HySecure?",
      "product": "HySecure",
      "ip": "127.0.0.1",
      "feedback": "positive"
    }
  ]
}
```

#### `GET /admin/top-questions`
```json
{
  "top_questions": [
    {
      "question": "How to install HySecure?",
      "product": "HySecure",
      "count": 12
    }
  ]
}
```

#### `GET /admin/download-csv`
Downloads `usage_logs.csv` file.

---

## ⚙️ How It Works

### End-to-End Flow

```
1. USER ASKS QUESTION
   ↓
   "What is HySecure Management Roles?"
   ↓
2. FRONTEND (index.html)
   - Display user message
   - Show "🤔 Thinking..."
   - POST /ask to backend
   ↓
3. BACKEND (main.py)
   - Receive question
   - Detect product: "hysecure" → HySecure
   - Call get_rag_answer(question)
   ↓
4. RAG ENGINE (rag.py)
   Step 1: Vector Search
   - Convert question to 384-dim vector
   - Search FAISS for 8 similar chunks
   
   Step 2: Product Filtering
   - Filter chunks where metadata.module = "HySecure"
   - Keep top 4 filtered results
   
   Step 3: Build Context
   - Combine chunks (max 800 chars each)
   
   Step 4: LLM Generation
   - Send context + question to GPT-4o-mini
   - Get answer
   
   Step 5: Confidence Check
   - Assess quality (0-1 score)
   - If < 0.6, add clarification request
   
   Step 6: Add Sources
   - Append source URLs
   ↓
5. LOGGING (usage_logger.py)
   - Generate response_id
   - Write to CSV: timestamp, question, product, IP, "", response_id
   ↓
6. RETURN TO FRONTEND
   - { answer: "...", response_id: "..." }
   ↓
7. FRONTEND DISPLAYS
   - Hide "🤔 Thinking..."
   - Show answer (markdown formatted)
   - Show sources as links
   - Add feedback buttons 👍 👎
   - Scroll to show start of answer
   ↓
8. USER CLICKS 👍
   - POST /feedback with response_id
   - Update CSV: feedback = "positive"
   ↓
9. ADMIN VIEWS
   - Login to admin.html
   - See stats, recent logs, feedback
```

---

## 🚀 Setup & Installation

### Prerequisites
```
Python 3.10+
pip
Virtual environment
OpenAI API key
```

### Step-by-Step

#### 1. Clone Repository
```bash
cd "d:\C BACKUP\rag-chat-widget"
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Packages installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - RAG framework
- `openai` - GPT-4o-mini API
- `sentence-transformers` - Embeddings
- `faiss-cpu` - Vector database
- `beautifulsoup4` - Web scraping
- `requests` - HTTP client

#### 4. Set Environment Variables
Create `.env` file:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### 5. Build Vector Database
```bash
python backend/ingest.py
```

**Output:**
```
🔍 Crawling links from: https://docs.accops.com/hysecure_7_2/index.html
✅ Discovered 150 documentation pages
✅ Created 3,278 document chunks
🎉 Vector database created successfully!
📦 Saved at: vector_store/accops_docs
```

#### 6. Start Backend Server
```bash
uvicorn backend.main:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### 7. Open Frontend
Open in browser:
```
file:///d:/C%20BACKUP/rag-chat-widget/frontend/index.html
```

Or use Live Server in VS Code.

#### 8. Test Chat
- Click orange chat button
- Ask: "What is HySecure?"
- See answer with sources
- Click 👍 or 👎

#### 9. Access Admin Dashboard
Open in browser:
```
file:///d:/C%20BACKUP/rag-chat-widget/admin/admin.html
```

Login with: `admin123`

---

## 📝 Configuration Files

### **`requirements.txt`**
Python dependencies:
```
fastapi>=0.95.0
uvicorn[standard]>=0.22.0
langchain>=0.0.300
openai>=0.27.0
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4
beautifulsoup4>=4.12.2
requests>=2.31.0
python-dotenv>=1.0.0
```

### **`.env`**
Environment variables:
```bash
OPENAI_API_KEY=sk-...
```

### **`.gitignore`**
Ignored files:
```
.env
.venv/
__pycache__/
*.pyc
data/usage_logs.csv
vector_store/
```

---

## 🎯 Key Improvements Made

### 1. Product-Aware Retrieval
**Before:** Mixed HySecure and HyWorks references  
**After:** Filters by product metadata for accurate answers

### 2. Larger Chunks
**Before:** 500 characters (fragmented content)  
**After:** 1200 characters (better context preservation)

### 3. Smart Scrolling
**Before:** Auto-scroll to bottom (shows sources first)  
**After:** Scroll to start of answer (shows main content first)

### 4. Thinking Indicator
**Before:** Plain dots  
**After:** "🤔 Thinking..." with animated dots

### 5. Feedback System
**Before:** No feedback collection  
**After:** 👍👎 buttons + admin dashboard analytics

### 6. Confidence-Based Clarification
**Before:** Generic "not found" errors  
**After:** Asks for specific details when uncertain

---

## 📊 Current Status

**Vector Database:**
- ✅ 3,278 document chunks
- ✅ HyWorks & HySecure docs indexed
- ✅ Metadata-based filtering enabled

**Backend:**
- ✅ FastAPI running on port 8000
- ✅ Product-aware RAG implemented
- ✅ Confidence assessment active
- ✅ Usage logging enabled

**Frontend:**
- ✅ Chat widget functional
- ✅ Thinking indicator working
- ✅ Feedback buttons active
- ✅ Smart scrolling enabled

**Admin:**
- ✅ Dashboard accessible
- ✅ Analytics working
- ✅ CSV download available
- ✅ Feedback tracking active

---

## 🎓 Learning Resources

### RAG (Retrieval-Augmented Generation)
RAG combines:
1. **Retrieval:** Find relevant documents from vector DB
2. **Augmentation:** Add context to user question
3. **Generation:** Use LLM to generate answer

**Why RAG?**
- More accurate than pure LLM (has specific knowledge)
- Cheaper than fine-tuning
- Citable sources
- Easy to update (just rebuild vector DB)

### Vector Databases (FAISS)
FAISS stores document chunks as vectors:
```
"HySecure roles..." → [0.12, -0.45, 0.78, ..., 0.33]  (384 dims)
"HyWorks setup..." → [0.09, 0.22, -0.11, ..., 0.54]
```

**Similarity search:**
```
User question: "What are roles?"
Question vector: [0.11, -0.43, 0.75, ..., 0.29]

Find closest vectors → Get original text → Send to LLM
```

### Embeddings
Sentence Transformers convert text to vectors:
```python
model = HuggingFaceEmbeddings("all-MiniLM-L6-v2")
vector = model.embed("What is HySecure?")
# Returns: array of 384 floats
```

---

## 🔧 Maintenance

### Rebuild Vector Database
When documentation is updated:
```bash
python backend/ingest.py
```

### Clear Logs
```bash
del data\usage_logs.csv
```

### Update Admin Key
Edit `admin/auth.py`:
```python
ADMIN_SECRET = "your-new-key"
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "Vector database not found"
```bash
# Rebuild it
python backend/ingest.py
```

### OpenAI API errors
```bash
# Check .env file
cat .env
# Should contain: OPENAI_API_KEY=sk-...

# Check API key validity at platform.openai.com
```

### Frontend can't connect
- Ensure backend is running: `uvicorn backend.main:app --reload`
- Check port 8000 is accessible
- Open browser console for CORS errors

---

## 📞 Support

For issues or questions:
1. Check logs in terminal
2. Check browser console (F12)
3. Review `data/usage_logs.csv` for query history
4. Rebuild vector database if needed

---

**Document Version:** 1.0  
**Last Updated:** January 25, 2026  
**Project Status:** ✅ Production Ready
