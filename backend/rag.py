import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from backend.product_definitions import PRODUCT_DEFINITIONS

VECTOR_DB_PATH = "vector_store/accops_docs"

_embeddings = None
_db = None


def get_embeddings():
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


# LOAD VECTOR DATABASE
def get_db():
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

# LLM INITIALIZATION 
def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        max_tokens=300      
    )

# CORE RAG FUNCTION
def get_rag_answer(question: str):
    
    question_lower = question.lower()
    target_product = None
    
    for product_key in PRODUCT_DEFINITIONS.keys():
        if product_key in question_lower:
            target_product = product_key
            break
    
    db = get_db()
    
    # Get more results initially to filter by product (with scores)
    all_docs_with_scores = db.similarity_search_with_score(question, k=8)
    
    if target_product:
        filtered_docs_with_scores = [
            (doc, score) for doc, score in all_docs_with_scores
            if doc.metadata.get("module", "").lower() == target_product.lower()
        ]
        # Fall back to unfiltered if no product-specific docs found
        docs_with_scores = filtered_docs_with_scores if filtered_docs_with_scores else all_docs_with_scores[:4]
    else:
        docs_with_scores = all_docs_with_scores[:4]

    if not docs_with_scores:
        return "Sorry, I couldn't find relevant information in the Accops documentation.", resolved_product or "unknown", 0.2

    # Extract docs from tuples for context building
    docs = [doc for doc, score in docs_with_scores]
    scores = [score for doc, score in docs_with_scores]

    context = "\n\n".join(doc.page_content[:800] for doc in docs)

    # Collect TOP 1-2 most relevant sources
    sources = []
    for doc in docs[:2]: 
        source = doc.metadata.get("source")
        if source and source not in sources:
            sources.append(source)

    resolved_product = target_product
    if not resolved_product:
        # Take module metadata from the top hit if available
        top_module = docs[0].metadata.get("module") if docs else None
        if top_module:
            resolved_product = top_module.lower()

    product_context = f"(Question is about: {target_product.upper()})" if target_product else ""
    
    prompt = f"""
You are an Accops documentation assistant. Answer the user's question clearly and concisely.

{product_context}

Rules:
- Use ONLY the documentation content below
- If the user asks in a specific language, respond in the SAME language. Otherwise, respond in English.
- Do NOT repeat the user's question
- If the question is about a specific product (HySecure or HyWorks), prioritize information from that product's documentation
- Format the answer clearly with proper line breaks
- Use **bold** for important terms
- If the answer is not present, say so clearly
- Keep the answer under 200 words

Documentation:
{context}

User Question: {question}

Answer:
"""

    # Call LLM (responsibly)
    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content.strip()

    #Append TOP sources (most relevant first)
    if sources:
        answer += "\n\n🔗 **Source(s):**\n"
        for src in sources:  # Already ordered by relevance
            answer += f"- {src}\n"

    #Calculate confidence score based on retrieval quality
    top_score = scores[0] if scores else 1.0
    avg_score = sum(scores) / len(scores) if scores else 1.0
    
    # Convert FAISS distance to confidence:
    confidence = max(0.2, min(0.95, 1.0 - (top_score * 0.5)))

    answer_lower = answer.lower()
    if any(phrase in answer_lower for phrase in 
           ["couldn't find", "not found", "unclear", "unable to", "no information", "don't have", "not available"]):
        confidence = max(0.2, confidence * 0.5)  # Halve confidence for uncertain answers
    
    # Boost confidence if there's a product match
    if target_product:
        # Check if we actually found product-specific docs
        product_docs_count = sum(1 for doc, score in docs_with_scores 
                                if doc.metadata.get("module", "").lower() == target_product.lower())
        if product_docs_count > 0:
            confidence = min(0.95, confidence + 0.15)
    
    return answer, resolved_product or "unknown", round(confidence, 2)
