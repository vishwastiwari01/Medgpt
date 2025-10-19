"""
Enhanced Document Preprocessing with Auto-Split for Large PDFs
Handles Harrison's and other large medical textbooks automatically
"""

import os
import pickle
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
from pdf_splitter import split_large_pdf

def load_documents(docs_folder=None, auto_split_pdfs=True, max_pdf_pages=200):
    """
    Load all documents from the documents folder
    Automatically splits large PDFs if enabled
    """
    script_dir = Path(__file__).parent.parent
    
    if docs_folder is None:
        docs_path = script_dir / "documents"
    else:
        docs_path = Path(docs_folder)
    
    docs_path = docs_path.resolve()
    
    if not docs_path.exists():
        print(f"❌ Documents folder not found at: {docs_path}")
        print(f"\n💡 Please create the documents folder at: {docs_path}")
        print("   Then add your PDF, TXT, or DOCX files to it.")
        
        try:
            docs_path.mkdir(parents=True, exist_ok=True)
            print(f"\n✓ Created documents folder at: {docs_path}")
        except Exception as e:
            print(f"   Could not create folder: {e}")
        
        return []
    
    documents = []
    processed_files = []
    
    # First, handle PDF splitting if enabled
    if auto_split_pdfs:
        print("\n🔍 Checking for large PDFs that need splitting...")
        pdf_files = list(docs_path.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(pdf_file))
                num_pages = len(reader.pages)
                
                if num_pages > max_pdf_pages:
                    print(f"\n📚 Large PDF detected: {pdf_file.name} ({num_pages} pages)")
                    print(f"   Splitting into chunks of {max_pdf_pages} pages...")
                    
                    split_files = split_large_pdf(str(pdf_file), max_pages=max_pdf_pages)
                    processed_files.extend(split_files)
                    print(f"   ✅ Split into {len(split_files)} parts")
                else:
                    processed_files.append(str(pdf_file))
            except Exception as e:
                print(f"   ⚠️ Error checking {pdf_file.name}: {e}")
                processed_files.append(str(pdf_file))
    
    # Load all documents
    all_files = []
    
    # Add split PDFs
    split_pdf_dir = docs_path / "split_pdfs"
    if split_pdf_dir.exists():
        all_files.extend(split_pdf_dir.glob("*.pdf"))
    
    # Add regular documents
    for ext in ['*.pdf', '*.txt', '*.docx']:
        all_files.extend(docs_path.glob(ext))
    
    # Remove duplicates
    all_files = list(set(all_files))
    
    print(f"\n📂 Loading {len(all_files)} file(s)...")
    
    for file_path in all_files:
        filename = file_path.name
        
        try:
            if filename.endswith('.pdf'):
                loader = PyPDFLoader(str(file_path))
            elif filename.endswith('.txt'):
                loader = TextLoader(str(file_path))
            elif filename.endswith('.docx'):
                loader = Docx2txtLoader(str(file_path))
            else:
                continue
            
            docs = loader.load()
            
            # Add enhanced metadata
            for doc in docs:
                doc.metadata['source'] = filename
                doc.metadata['file_path'] = str(file_path)
                doc.metadata['original_file'] = filename.split('_part')[0] if '_part' in filename else filename
            
            documents.extend(docs)
            print(f"   ✓ Loaded {filename} ({len(docs)} pages)")
            
        except Exception as e:
            print(f"   ✗ Error loading {filename}: {e}")
    
    return documents

def create_chunks(documents, chunk_size=500, chunk_overlap=50):
    """
    Split documents into chunks for better retrieval
    Optimized for medical literature
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks from {len(documents)} documents")
    
    return chunks

def create_vectorstore(chunks, save_path=None):
    """Create and save FAISS vectorstore"""
    script_dir = Path(__file__).parent.parent
    
    if save_path is None:
        save_path_abs = script_dir / "vectorstore"
    else:
        save_path_abs = Path(save_path)
    
    save_path_abs = save_path_abs.resolve()
    save_path_abs.mkdir(parents=True, exist_ok=True)
    
    print("\n🔨 Creating embeddings (this may take a few minutes)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    print("   Building FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save vectorstore
    vectorstore.save_local(str(save_path_abs))
    print(f"   ✓ Vectorstore saved to {save_path_abs}")
    
    # Save chunks metadata separately
    chunks_metadata = [
        {
            'content': chunk.page_content,
            'source': chunk.metadata.get('source', 'unknown'),
            'page': chunk.metadata.get('page', 0),
            'file_path': chunk.metadata.get('file_path', ''),
            'original_file': chunk.metadata.get('original_file', '')
        }
        for chunk in chunks
    ]
    
    with open(save_path_abs / "chunks_metadata.pkl", 'wb') as f:
        pickle.dump(chunks_metadata, f)
    print(f"   ✓ Chunks metadata saved")
    
    return vectorstore

def main():
    print("=" * 70)
    print(" 🩺 MedGPT Document Preprocessing with Auto-Split")
    print("=" * 70)
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Create directories
    docs_dir = project_root / "documents"
    vectorstore_dir = project_root / "vectorstore"
    
    docs_dir.mkdir(exist_ok=True)
    vectorstore_dir.mkdir(exist_ok=True)
    
    print(f"\n📂 Project structure:")
    print(f"   Project root: {project_root}")
    print(f"   Documents folder: {docs_dir}")
    print(f"   Vectorstore folder: {vectorstore_dir}")
    
    # Load documents with auto-split
    print("\n" + "-" * 70)
    print("Step 1: Loading & Splitting Documents")
    print("-" * 70)
    
    documents = load_documents(
        docs_dir,
        auto_split_pdfs=True,  # Enable automatic PDF splitting
        max_pdf_pages=200      # Split PDFs larger than 200 pages
    )
    
    if not documents:
        print("\n❌ No documents found!")
        print(f"   Please add PDF, TXT, or DOCX files to: {docs_dir}")
        print("\n💡 Tips:")
        print("   • Large PDFs (like Harrison's) will be automatically split")
        print("   • Supported formats: PDF, TXT, DOCX")
        print("   • Place files directly in the documents/ folder")
        return
    
    # Create chunks
    print("\n" + "-" * 70)
    print("Step 2: Creating Text Chunks")
    print("-" * 70)
    chunks = create_chunks(documents)
    
    # Create and save vectorstore
    print("\n" + "-" * 70)
    print("Step 3: Building Vector Index")
    print("-" * 70)
    vectorstore = create_vectorstore(chunks, vectorstore_dir)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ PREPROCESSING COMPLETE!")
    print("=" * 70)
    
    print(f"\n📊 Summary:")
    print(f"   Total documents processed: {len(documents)}")
    print(f"   Total chunks created: {len(chunks)}")
    print(f"   Vectorstore location: {vectorstore_dir}")
    print(f"   Index size: {vectorstore.index.ntotal:,} vectors")
    
    # Check for split PDFs
    split_pdf_dir = docs_dir / "split_pdfs"
    if split_pdf_dir.exists():
        split_count = len(list(split_pdf_dir.glob("*.pdf")))
        if split_count > 0:
            print(f"\n📚 Large PDF Processing:")
            print(f"   Split PDFs created: {split_count}")
            print(f"   Location: {split_pdf_dir}")
    
    print(f"\n🚀 Next step:")
    print(f"   Run: streamlit run app.py")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()