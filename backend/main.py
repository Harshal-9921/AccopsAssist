from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from backend.rag import get_rag_answer
from admin.admin_api import router as admin_router
from admin.usage_logger import log_usage, log_feedback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

class Feedback(BaseModel):
    response_id: str
    feedback: str  

@app.post("/ask")
def ask_question(q: Question, request: Request):
    try:
        answer, resolved_product, confidence_score = get_rag_answer(q.question)
    except Exception as e:
        # Check for authentication error (string matching since we might not import the specific exception class)
        error_msg = str(e).lower()
        if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
             return {"answer": "⚠️ **Authentication Error:** Invalid OpenAI API Key. Please check your `.env` file.", "response_id": "error-auth"}
        
        print(f"RAG Error: {e}")
        return {"answer": "⚠️ **System Error:** An error occurred while processing your request.", "response_id": "error-sys"}

    #Detect product
    q_lower = q.question.lower()
    if "hyworks" in q_lower:
        product = "HyWorks"
    elif "hysecure" in q_lower:
        product = "HySecure"
    else:
        product = resolved_product.capitalize() if resolved_product else "Unknown"

    ip = request.client.host

    #LOG TO CSV and get response_id
    try:
        response_id = log_usage(
            question=q.question,
            product=product,
            ip=ip,
            confidence_score=confidence_score
        )
    except:
        response_id = "log-failed"

    return {"answer": answer, "response_id": response_id}

@app.post("/feedback")
def submit_feedback(fb: Feedback):
    """Endpoint to receive user feedback"""
    log_feedback(fb.response_id, fb.feedback)
    return {"status": "success", "message": "Feedback recorded"}

# Admin routes
app.include_router(admin_router)

# Serve Frontend
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

# Serve Admin UI
@app.get("/admin-ui")
async def serve_admin_ui():
    return FileResponse("admin/admin.html")
