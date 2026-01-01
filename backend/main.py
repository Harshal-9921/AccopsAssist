from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.rag import get_rag_answer
from admin.admin_api import router as admin_router
from admin.usage_logger import log_usage

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

@app.post("/ask")
def ask_question(q: Question, request: Request):
    answer = get_rag_answer(q.question)

    # 🔹 Detect product (simple logic)
    product = "HyWorks" if "hyworks" in q.question.lower() else "HySecure"

    # 🔹 Get user IP
    ip = request.client.host

    # 🔹 LOG TO CSV
    log_usage(
        question=q.question,
        product=product,
        ip=ip
    )

    return {"answer": answer}

# Admin routes
app.include_router(admin_router)
