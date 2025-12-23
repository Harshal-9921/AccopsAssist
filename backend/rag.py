import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from product_definitions import PRODUCT_DEFINITIONS



# ======================================================
# LOAD EMBEDDINGS (LOCAL, NO API COST)
# ======================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ======================================================
# LOAD VECTOR DATABASE
# ======================================================

VECTOR_DB_PATH = "vector_store/accops_docs"

if not os.path.exists(VECTOR_DB_PATH):
    raise RuntimeError(
        f"Vector database not found at '{VECTOR_DB_PATH}'. "
        "Run ingest.py first."
    )

db = FAISS.load_local(
    VECTOR_DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# ======================================================
# LAZY LLM INITIALIZATION (RESPONSIBLE USE)
# ======================================================

def get_llm():
    """
    Lazily initialize the LLM to:
    - avoid startup crashes
    - minimize API usage
    """
    return ChatOpenAI(
        model="gpt-4o-mini",   # ✅ REQUIRED BY TEAM LEAD
        temperature=0,
        max_tokens=300         # ✅ COST CONTROL
    )

# ======================================================
# CORE RAG FUNCTION
# ======================================================
def is_definition_question(question: str) -> bool:
    question = question.lower().strip()
    return question.startswith("what is") or question.startswith("what are")


def get_rag_answer(question: str) -> str:
    q_lower = question.lower().strip()

    # 1️⃣ Product definition override (SAFE EXIT)
    for product, data in PRODUCT_DEFINITIONS.items():
        if q_lower == f"what is {product}?" or q_lower.startswith(f"what is {product}"):
            return (
                f"{data['answer']}\n\n"
                f"🔗 **Source:**\n{data['source']}"
            )

    # 2️⃣ Normal RAG flow (docs ALWAYS defined)
    docs = db.max_marginal_relevance_search(
        question,
        k=4,
        fetch_k=12
    )

    if not docs:
        return "Sorry, I couldn’t find relevant information in the Accops documentation."

    # 3️⃣ Build context
    context = "\n\n".join(doc.page_content[:800] for doc in docs)

    # 4️⃣ Primary source
    primary_source = docs[0].metadata.get("source")

    # 5️⃣ Prompt
    prompt = f"""
You are an Accops documentation assistant.

Provide a clear, helpful explanation based on the documentation below.
- Do NOT repeat the user's question
- Keep the answer concise and professional

Documentation Context:
{context}

Answer:
"""

    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content.strip()

    # 6️⃣ Attach source
    if primary_source:
        answer += f"\n\n🔗 **Source:**\n{primary_source}"

    return answer
