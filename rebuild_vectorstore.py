"""
Rebuild Vectorstore with File Paths
"""
import sys
from pathlib import Path
import fitz
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = "vectorstore"

def extract_text_from_pdf(pdf_path: Path):
    documents = []
    doc = fitz.open(str(pdf_path))
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_num,
                        "file_path": str(pdf_path.absolute()),
                        "total_pages": len(doc)
                    }
                )
            )
    
    doc.close()
    return documents

def build_vectorstore(pdf_directory="documents"):
    pdf_dir = Path(pdf_directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDFs")
    
    all_documents = []
    for pdf in pdf_files:
        print(f"Processing: {pdf.name}")
        all_documents.extend(extract_text_from_pdf(pdf))
    
    print(f"Total documents: {len(all_documents)}")
    print("Creating vectorstore...")
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(all_documents, embeddings)
    
    Path(VECTORSTORE_DIR).mkdir(exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)
    
    print("✅ Done!")

if __name__ == "__main__":
    build_vectorstore()
