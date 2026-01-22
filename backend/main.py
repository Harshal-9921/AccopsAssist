from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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
    feedback: str  # "positive" or "negative"

@app.post("/ask")
def ask_question(q: Question, request: Request):
    answer = get_rag_answer(q.question)

    # 🔹 Detect product (simple logic)
    product = "HyWorks" if "hyworks" in q.question.lower() else "HySecure"

    # 🔹 Get user IP
    ip = request.client.host

    # 🔹 LOG TO CSV and get response_id
    response_id = log_usage(
        question=q.question,
        product=product,
        ip=ip
    )

    return {"answer": answer, "response_id": response_id}

@app.post("/feedback")
def submit_feedback(fb: Feedback):
    """Endpoint to receive user feedback"""
    log_feedback(fb.response_id, fb.feedback)
    return {"status": "success", "message": "Feedback recorded"}

# Admin routes
app.include_router(admin_router)
