import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


#CONFIGURATION

SEED_URLS = [
    "https://docs.accops.com/HyWorks36/index.html",
    "https://docs.accops.com/hysecure_7_2/index.html"
]

BASE_DOMAIN = "docs.accops.com"
OUTPUT_DIR = "vector_store/accops_docs"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150


#HELPERS
def is_valid_doc_link(url: str) -> bool:
    """
    Allow only Accops HTML documentation pages.
    """
    parsed = urlparse(url)
    if BASE_DOMAIN not in parsed.netloc:
        return False
    if not url.endswith(".html"):
        return False
    return True


def extract_links(page_url: str) -> set:
    """
    Extract all internal documentation links from a page.
    """
    print(f"🔍 Crawling links from: {page_url}")
    res = requests.get(page_url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(page_url, href)

        if is_valid_doc_link(full_url):
            links.add(full_url)

    return links


def scrape_page(url: str) -> str:
    """
    Extract clean readable text from a documentation page.
    """
    print(f"📄 Scraping: {url}")
    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())

# MAIN INGESTION PIPELINE
def main():
    #Discover all documentation pages
    all_urls = set()

    for seed in SEED_URLS:
        discovered = extract_links(seed)
        all_urls.update(discovered)

    print(f"\n✅ Discovered {len(all_urls)} documentation pages\n")

    #Scrape + chunk pages with metadata
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    documents = []

    for url in sorted(all_urls):
        try:
            text = scrape_page(url)
            chunks = splitter.split_text(text)

            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": url,
                            "module": "HySecure" if "hysecure" in url.lower() else "HyWorks"
                        }
                    )
                )
        except Exception as e:
            print(f"⚠️ Failed to process {url}: {e}")

    print(f"\n✅ Created {len(documents)} document chunks\n")

    # Create embeddings (LOCAL, NO API COST)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Build FAISS vector database
    db = FAISS.from_documents(documents, embeddings)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    db.save_local(OUTPUT_DIR)

    print("🎉 Vector database created successfully!")
    print(f"📦 Saved at: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()