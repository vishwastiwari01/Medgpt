"""
MedGPT Diagnostic Tool
Run this to check API keys, file paths, and vectorstore
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(page_title="MedGPT Diagnostics", page_icon="🔧", layout="wide")

st.title("🔧 MedGPT Diagnostic Tool")
st.markdown("---")

# Check 1: LLM Handler
st.header("1️⃣ LLM Backend Check")

try:
    from llm_handler import LLMHandler
    
    handler = LLMHandler()
    status = handler.get_status()
    
    st.json(status)
    
    backend = status.get("backend", "unknown")
    
    if backend in ["groq", "openai", "ollama"]:
        st.success(f"✅ LLM Backend: {backend}")
    else:
        st.error(f"❌ LLM Backend: {backend} (Limited Mode)")
        
        st.warning("**How to fix:**")
        st.markdown("""
        1. Check if you have API keys set up
        2. Create `.streamlit/secrets.toml` file with:
        ```toml
        GROQ_API_KEY = "your-key-here"
        # or
        OPENAI_API_KEY = "your-key-here"
        ```
        3. Or use Ollama locally
        """)
        
except Exception as e:
    st.error(f"❌ Error loading LLM Handler: {e}")

st.markdown("---")

# Check 2: Vectorstore
st.header("2️⃣ Vectorstore Check")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    
    vectorstore_path = Path("vectorstore")
    
    if not vectorstore_path.exists():
        st.error("❌ Vectorstore directory not found")
        st.info("Run `python build_cache.py` to create it")
    else:
        st.success(f"✅ Vectorstore directory exists: {vectorstore_path}")
        
        # Check files
        files = list(vectorstore_path.glob("*"))
        st.write("**Files found:**")
        for f in files:
            st.write(f"- {f.name} ({f.stat().st_size / 1024:.1f} KB)")
        
        # Try loading
        try:
            emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vs = FAISS.load_local(str(vectorstore_path), emb, allow_dangerous_deserialization=True)
            
            st.success(f"✅ Loaded vectorstore with {vs.index.ntotal:,} chunks")
            
            # Sample a document to check metadata
            st.subheader("📄 Sample Document Metadata")
            
            sample_docs = vs.similarity_search("test", k=1)
            
            if sample_docs:
                doc = sample_docs[0]
                st.write("**Metadata:**")
                st.json(doc.metadata)
                
                # Check file_path
                file_path = doc.metadata.get("file_path", "")
                
                if not file_path:
                    st.error("❌ **PROBLEM FOUND:** `file_path` is missing in metadata!")
                    st.warning("""
                    **This is why PDF preview fails!**
                    
                    To fix:
                    1. Your vectorstore was built without file paths
                    2. You need to rebuild it with proper file paths
                    """)
                else:
                    st.success(f"✅ file_path found: {file_path}")
                    
                    # Check if file exists
                    if Path(file_path).exists():
                        st.success(f"✅ PDF file exists at: {file_path}")
                    else:
                        st.error(f"❌ PDF file NOT found at: {file_path}")
                        
                        # Try to find PDF files
                        st.info("**Looking for PDF files in project...**")
                        pdf_files = list(Path(".").rglob("*.pdf"))
                        if pdf_files:
                            st.write("Found these PDFs:")
                            for pdf in pdf_files:
                                st.write(f"- {pdf}")
                        else:
                            st.warning("No PDF files found in project")
                
            else:
                st.warning("No documents found in vectorstore")
                
        except Exception as e:
            st.error(f"❌ Error loading vectorstore: {e}")
            
except Exception as e:
    st.error(f"❌ Error: {e}")

st.markdown("---")

# Check 3: API Keys
st.header("3️⃣ API Keys Check")

secrets_file = Path(".streamlit/secrets.toml")

if secrets_file.exists():
    st.success("✅ secrets.toml file exists")
    
    try:
        with open(secrets_file) as f:
            content = f.read()
        
        # Check for keys (without showing actual values)
        if "GROQ_API_KEY" in content:
            st.success("✅ GROQ_API_KEY found")
        else:
            st.info("ℹ️ GROQ_API_KEY not found")
        
        if "OPENAI_API_KEY" in content:
            st.success("✅ OPENAI_API_KEY found")
        else:
            st.info("ℹ️ OPENAI_API_KEY not found")
            
        if "OLLAMA_HOST" in content:
            st.success("✅ OLLAMA_HOST found")
        else:
            st.info("ℹ️ OLLAMA_HOST not found")
            
    except Exception as e:
        st.error(f"Error reading secrets: {e}")
else:
    st.error("❌ secrets.toml file NOT found")
    st.warning("""
    **Create this file:** `.streamlit/secrets.toml`
    
    ```toml
    # For Groq (Recommended - Free and Fast)
    GROQ_API_KEY = "gsk_..."
    
    # OR for OpenAI
    OPENAI_API_KEY = "sk-..."
    
    # OR for Ollama (Local)
    OLLAMA_HOST = "http://localhost:11434"
    ```
    """)

st.markdown("---")

# Check 4: PDF Files
st.header("4️⃣ PDF Files Check")

pdf_files = list(Path(".").rglob("*.pdf"))

if pdf_files:
    st.success(f"✅ Found {len(pdf_files)} PDF files")
    
    for pdf in pdf_files[:10]:  # Show first 10
        st.write(f"📄 {pdf}")
        st.caption(f"Size: {pdf.stat().st_size / 1024 / 1024:.2f} MB")
else:
    st.warning("⚠️ No PDF files found in project directory")

st.markdown("---")

# Check 5: Upload Handler
st.header("5️⃣ Upload Handler Check")

try:
    from upload_handler import render_upload_ui
    st.success("✅ upload_handler.py found")
except Exception as e:
    st.error(f"❌ Error importing upload_handler: {e}")

st.markdown("---")

# Summary
st.header("📊 Summary & Recommendations")

issues = []

# Check backend
try:
    handler = LLMHandler()
    if handler.backend not in ["groq", "openai", "ollama"]:
        issues.append("🔴 LLM Backend in limited mode - need API keys")
except:
    issues.append("🔴 LLM Handler not working")

# Check vectorstore metadata
try:
    vs = FAISS.load_local("vectorstore", HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"), allow_dangerous_deserialization=True)
    docs = vs.similarity_search("test", k=1)
    if docs and not docs[0].metadata.get("file_path"):
        issues.append("🔴 Vectorstore missing file_path metadata - PDF preview won't work")
except:
    issues.append("🔴 Vectorstore not accessible")

if issues:
    st.error("**Issues Found:**")
    for issue in issues:
        st.write(issue)
else:
    st.success("✅ All checks passed!")

st.markdown("---")
st.caption("Run: `streamlit run diagnostic.py`")