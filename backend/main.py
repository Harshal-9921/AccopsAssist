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
    feedback: str  

@app.post("/ask")
def ask_question(q: Question, request: Request):
    answer, resolved_product, confidence_score = get_rag_answer(q.question)

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
    response_id = log_usage(
        question=q.question,
        product=product,
        ip=ip,
        confidence_score=confidence_score
    )

    return {"answer": answer, "response_id": response_id}

@app.post("/feedback")
def submit_feedback(fb: Feedback):
    """Endpoint to receive user feedback"""
    log_feedback(fb.response_id, fb.feedback)
    return {"status": "success", "message": "Feedback recorded"}

# Admin routes
app.include_router(admin_router)
