"""
Preprocess all medical documents → build FAISS vectorstore
Usage:  python preprocess_documents.py
"""

import os
import pickle
from pathlib import Path

# ✅ Use the modern embedding import when available
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings  # fallback

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DOCS_DIR = "documents"
VS_DIR = "vectorstore"

def load_documents(docs_folder=DOCS_DIR):
    docs = []
    p = Path(docs_folder)
    p.mkdir(exist_ok=True)
    for filename in os.listdir(p):
        fp = p / filename
        try:
            if filename.lower().endswith(".pdf"):
                loader = PyPDFLoader(str(fp))
            elif filename.lower().endswith(".txt"):
                loader = TextLoader(str(fp))
            elif filename.lower().endswith(".docx"):
                loader = Docx2txtLoader(str(fp))
            else:
                continue
            items = loader.load()
            for d in items:
                d.metadata["source"] = filename
                d.metadata["file_path"] = str(fp)
            docs.extend(items)
            print(f"✓ Loaded {filename}")
        except Exception as e:
            print(f"✗ Error loading {filename}: {e}")
    return docs

def create_chunks(documents, chunk_size=500, overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"✓ Created {len(chunks)} chunks from {len(documents)} docs")
    return chunks

def create_vectorstore(chunks, save_path=VS_DIR):
    os.makedirs(save_path, exist_ok=True)
    emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    print("🔧 Building FAISS index ...")
    vs = FAISS.from_documents(chunks, emb)
    vs.save_local(save_path)
    print(f"✓ Vectorstore saved to '{save_path}'")

    meta = [{
        "content": ch.page_content[:500],
        "source": ch.metadata.get("source", "unknown"),
        "page": ch.metadata.get("page", 0),
        "file_path": ch.metadata.get("file_path", ""),
    } for ch in chunks]
    with open(Path(save_path) / "chunks_metadata.pkl", "wb") as f:
        pickle.dump(meta, f)
    print(f"✓ Metadata saved ({len(meta)} entries)")
    return vs

def main():
    print("\n=== Medical Document Preprocessing ===\n")
    documents = load_documents(DOCS_DIR)
    if not documents:
        print("⚠️  No documents found in ./documents")
        return
    chunks = create_chunks(documents)
    create_vectorstore(chunks)
    print("\n✅ Done! You can now run:  streamlit run app.py\n")

if __name__ == "__main__":
    main()
