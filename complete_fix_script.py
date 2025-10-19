"""
Complete Fix Script for MedGPT
Fixes all issues: imports, vectorstore, and generates setup instructions
"""

import sys
from pathlib import Path
import shutil
from datetime import datetime

def check_and_fix_imports():
    """Fix import statements in app.py"""
    print("=" * 70)
    print("1️⃣ CHECKING IMPORTS")
    print("=" * 70)
    
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ app.py not found!")
        return False
    
    content = app_file.read_text(encoding='utf-8')
    
    # Check for wrong import
    if "from llm_handler import LLMHandler" in content:
        print("⚠️ Found incorrect import: 'from llm_handler import LLMHandler'")
        
        # Backup
        backup_file = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy(app_file, backup_file)
        print(f"📦 Created backup: {backup_file}")
        
        # Fix
        content = content.replace(
            "from llm_handler import LLMHandler",
            "from utils.llm_handler import LLMHandler"
        )
        
        app_file.write_text(content, encoding='utf-8')
        print("✅ Fixed import statement")
        return True
    elif "from utils.llm_handler import LLMHandler" in content:
        print("✅ Import is already correct")
        return True
    else:
        print("⚠️ Could not find LLMHandler import")
        return False

def check_secrets():
    """Check if secrets.toml exists and has API key"""
    print("\n" + "=" * 70)
    print("2️⃣ CHECKING API KEYS")
    print("=" * 70)
    
    secrets_dir = Path(".streamlit")
    secrets_file = secrets_dir / "secrets.toml"
    
    if not secrets_dir.exists():
        print("📁 Creating .streamlit directory...")
        secrets_dir.mkdir(exist_ok=True)
    
    if not secrets_file.exists():
        print("📝 Creating secrets.toml template...")
        secrets_content = """# MedGPT API Configuration
# Get your free Groq API key from: https://console.groq.com/keys

GROQ_API_KEY = "gsk_YOUR_KEY_HERE"

# Alternative: OpenAI (if you prefer)
# OPENAI_API_KEY = "sk_YOUR_KEY_HERE"

# Alternative: Ollama (local, no API key needed)
# OLLAMA_HOST = "http://localhost:11434"
"""
        secrets_file.write_text(secrets_content, encoding='utf-8')
        print("✅ Created .streamlit/secrets.toml")
        print("⚠️ YOU MUST EDIT THIS FILE AND ADD YOUR API KEY!")
        return False
    else:
        content = secrets_file.read_text(encoding='utf-8')
        if "gsk_" in content and "YOUR_KEY_HERE" not in content:
            print("✅ Groq API key found")
            return True
        elif "sk-" in content and "YOUR_KEY_HERE" not in content:
            print("✅ OpenAI API key found")
            return True
        else:
            print("⚠️ No valid API key found in secrets.toml")
            print("   Edit .streamlit/secrets.toml and add your key")
            return False

def check_vectorstore():
    """Check if vectorstore has proper metadata"""
    print("\n" + "=" * 70)
    print("3️⃣ CHECKING VECTORSTORE")
    print("=" * 70)
    
    vs_dir = Path("vectorstore")
    
    if not vs_dir.exists():
        print("❌ Vectorstore directory not found")
        return False
    
    required_files = ["index.faiss", "index.pkl"]
    missing = [f for f in required_files if not (vs_dir / f).exists()]
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ Vectorstore files exist")
    
    # Try to load and check metadata
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        
        emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vs = FAISS.load_local(str(vs_dir), emb, allow_dangerous_deserialization=True)
        
        # Check metadata
        docs = vs.similarity_search("test", k=1)
        if docs and "file_path" in docs[0].metadata:
            print(f"✅ Vectorstore has file_path metadata")
            print(f"   Example: {docs[0].metadata.get('file_path')}")
            return True
        else:
            print("⚠️ Vectorstore missing file_path metadata")
            print("   Need to rebuild for PDF preview to work")
            return False
            
    except Exception as e:
        print(f"⚠️ Could not verify vectorstore: {e}")
        return False

def check_documents():
    """Check if PDF documents exist"""
    print("\n" + "=" * 70)
    print("4️⃣ CHECKING PDF DOCUMENTS")
    print("=" * 70)
    
    doc_dir = Path("documents")
    
    if not doc_dir.exists():
        print("❌ Documents directory not found")
        return False
    
    pdf_files = list(doc_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in documents/")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files")
    for pdf in pdf_files[:5]:
        print(f"   - {pdf.name}")
    if len(pdf_files) > 5:
        print(f"   ... and {len(pdf_files) - 5} more")
    
    return True

def generate_rebuild_script():
    """Generate rebuild_vectorstore.py if it doesn't exist"""
    print("\n" + "=" * 70)
    print("5️⃣ CHECKING REBUILD SCRIPT")
    print("=" * 70)
    
    rebuild_file = Path("rebuild_vectorstore.py")
    
    if rebuild_file.exists():
        print("✅ rebuild_vectorstore.py exists")
        return True
    
    print("📝 Creating rebuild_vectorstore.py...")
    
    script_content = '''"""
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
'''
    
    rebuild_file.write_text(script_content, encoding='utf-8')
    print("✅ Created rebuild_vectorstore.py")
    return True

def print_summary(results):
    """Print summary and next steps"""
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    all_good = all(results.values())
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS")
    print("=" * 70)
    
    if not results["API Keys"]:
        print("\n1. Add your Groq API key:")
        print("   - Get free key from: https://console.groq.com/keys")
        print("   - Edit: .streamlit/secrets.toml")
        print("   - Replace: gsk_YOUR_KEY_HERE with your actual key")
    
    if not results["Vectorstore Metadata"]:
        print("\n2. Rebuild vectorstore with file paths:")
        print("   python rebuild_vectorstore.py")
    
    if all_good:
        print("\n✅ Everything looks good!")
        print("\n🚀 Run your app:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️ Fix the issues above, then run:")
        print("   streamlit run app.py")

def main():
    print("\n")
    print("🔧 MedGPT Complete Fix Tool")
    print("=" * 70)
    print()
    
    results = {
        "Imports": check_and_fix_imports(),
        "API Keys": check_secrets(),
        "Vectorstore Files": check_vectorstore() is not False,
        "Vectorstore Metadata": check_vectorstore(),
        "PDF Documents": check_documents(),
        "Rebuild Script": generate_rebuild_script()
    }
    
    print_summary(results)

if __name__ == "__main__":
    main()
