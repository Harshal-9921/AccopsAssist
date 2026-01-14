import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI


# ======================================================
# CONFIG / LAZY INITIALIZATION
# ======================================================

VECTOR_DB_PATH = "vector_store/accops_docs"

# Internal caches (initialized on first use to avoid import-time downloads)
_embeddings = None
_db = None


def get_embeddings():
    """Lazily initialize and return HuggingFace embeddings.

    This avoids trying to download the model during module import (which
    causes the server to fail to start in offline/DNS-failure environments).
    """
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            raise RuntimeError(
                "Failed to initialize local HuggingFace embeddings. "
                "This usually means the model couldn’t be downloaded (offline/DNS issue). "
                "To fix: run `python backend/ingest.py` on a machine with internet to build the vector DB, "
                "or pre-download the model into your Hugging Face cache, or set HUGGINGFACE_HUB_CACHE/HF_HOME to a cache containing the model. "
                f"Original error: {e}"
            ) from e
    return _embeddings

# ======================================================
# LOAD VECTOR DATABASE
# ======================================================

def get_db():
    """Lazily load and return the FAISS vector DB (caches result)."""
    global _db
    if _db is None:
        if not os.path.exists(VECTOR_DB_PATH):
            raise RuntimeError(
                f"Vector database not found at '{VECTOR_DB_PATH}'. Run `python backend/ingest.py` to build it."
            )
        embeddings = get_embeddings()
        _db = FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return _db

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

def get_rag_answer(question: str) -> str:
    """
    RAG-based answer using:
    - FAISS retrieval
    - gpt-4o-mini for final answer
    """

    # 1️⃣ Retrieve relevant chunks (load DB lazily)
    db = get_db()
    docs = db.similarity_search(question, k=4)

    if not docs:
        return "Sorry, I couldn’t find relevant information in the Accops documentation."

    # 2️⃣ Build compact context (limit size = responsible use)
    context = "\n\n".join(doc.page_content[:800] for doc in docs)

    # 3️⃣ Collect unique sources
    sources = {
        doc.metadata.get("source")
        for doc in docs
        if doc.metadata.get("source")
    }

    # 4️⃣ Strict, low-token prompt
    prompt = f"""
You are an Accops documentation assistant.

Rules:
- Use ONLY the documentation content below
- Do NOT repeat the user's question
- Be concise and factual
- If the answer is not present, say so clearly

Documentation:
{context}

Answer:
"""

    # 5️⃣ Call LLM (responsibly)
    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content.strip()

    # 6️⃣ Append sources
    if sources:
        answer += "\n\n🔗 **Source:**\n"
        for src in sources:
            answer += f"- {src}\n"

    return answer
