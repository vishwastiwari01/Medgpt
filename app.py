"""
MedGPT - Professional Medical RAG Assistant
Polished UI with better colors and UX
FIXED: PDF Preview & Fallback Issues
"""

import os
import time
from pathlib import Path
import sys
import base64  # ADDED: For PDF preview fix

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "utils"))

import streamlit as st
import fitz  # PyMuPDF

# LangChain
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS

# Project utils
from upload_handler import render_upload_ui
from utils.llm_handler import LLMHandler

# Constants
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = "vectorstore"
TOP_K = 3

# Page config
st.set_page_config(
    page_title="MedGPT",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

# Beautiful medical-themed styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* Main background - soft medical blue */
.main {
    background: linear-gradient(135deg, #f0f4f8 0%, #e8eff5 100%);
}

/* Header */
.main-header {
    font-size: 2.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.5rem;
    padding-top: 1rem;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* Message bubbles */
.query-bubble {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 16px 16px 4px 16px;
    margin: 1rem 0;
    box-shadow: 0 2px 12px rgba(59, 130, 246, 0.3);
}

.response-bubble {
    background: white;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #3b82f6;
    padding: 1.5rem;
    border-radius: 4px 16px 16px 16px;
    margin: 1rem 0;
    line-height: 1.8;
    color: #1f2937;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* PDF viewer - scrollable container */
.pdf-viewer-container {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pdf-header {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    padding: 1rem 1.5rem;
    font-weight: 600;
    font-size: 1.05rem;
    position: sticky;
    top: 0;
    z-index: 10;
}

.pdf-scroll-area {
    max-height: 600px;
    overflow-y: auto;
    padding: 1rem;
}

/* Highlight box */
.highlight-box {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-left: 4px solid #f59e0b;
    padding: 1rem 1.25rem;
    border-radius: 8px;
    color: #78350f;
    line-height: 1.8;
    margin: 1rem 0;
}

/* Timing info - hide warning if Groq works */
.timing-info {
    display: inline-block;
    background: #f3f4f6;
    color: #6b7280;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #9ca3af;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

.empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s;
    border: 1px solid #e5e7eb;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Hide elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {visibility: hidden;}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f3f4f6;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #1e40af;
}
</style>
""", unsafe_allow_html=True)

# Cached resources
@st.cache_resource(show_spinner=False)
def load_vectorstore():
    path = Path(VECTORSTORE_DIR)
    if not path.exists():
        st.error("❌ Knowledge base not found")
        st.stop()
    emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vs = FAISS.load_local(str(path), emb, allow_dangerous_deserialization=True)
    return vs

@st.cache_resource(show_spinner=False)
def get_retriever():
    vs = load_vectorstore()
    return vs, vs.as_retriever(search_kwargs={"k": TOP_K})

@st.cache_resource(show_spinner=False)
def get_llm_handler():
    return LLMHandler()

# FIXED: PDF preview with base64 encoding
def display_pdf_base64(pdf_path, page_num=None):
    """Display PDF using base64 encoding - works reliably in browsers"""
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Convert to base64
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Create iframe
        pdf_html = f'''
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}#page={page_num+1 if page_num is not None else 1}" 
                width="100%" 
                height="800px" 
                type="application/pdf"
                style="border: 1px solid #e5e7eb; border-radius: 8px;">
                <p>Your browser does not support inline PDF viewing. 
                   <a href="data:application/pdf;base64,{base64_pdf}" download>Download PDF</a>
                </p>
            </iframe>
        '''
        
        st.markdown(pdf_html, unsafe_allow_html=True)
        return True
        
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")
        return False

# PDF preview - scrollable single page view (IMPROVED)
def display_pdf_page_scrollable(pdf_path, page_num, highlight_text=None):
    """Display single PDF page in scrollable container with fallback to base64"""
    doc = None
    try:
        doc = fitz.open(pdf_path)
        total = len(doc)
        
        if not isinstance(page_num, int) or page_num >= total:
            page_num = 0
        
        page = doc[page_num]
        
        # Highlight
        if highlight_text:
            snippet = highlight_text[:120].strip()
            if snippet:
                try:
                    for inst in page.search_for(snippet)[:3]:
                        page.add_highlight_annot(inst)
                except:
                    pass
        
        # Render
        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
        
        st.markdown(f'<div class="pdf-scroll-area">', unsafe_allow_html=True)
        st.image(pix.tobytes("png"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if page_num > 0 and st.button("◀ Previous", use_container_width=True):
                st.session_state.current_page = page_num - 1
                st.rerun()
        with col2:
            st.caption(f"Page {page_num + 1} of {total}")
        with col3:
            if page_num < total - 1 and st.button("Next ▶", use_container_width=True):
                st.session_state.current_page = page_num + 1
                st.rerun()
        
        doc.close()
        return True
        
    except Exception as e:
        # Fallback to base64 display
        if doc:
            doc.close()
        st.warning(f"PyMuPDF rendering failed, using alternative viewer...")
        return display_pdf_base64(pdf_path, page_num)

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_source" not in st.session_state:
    st.session_state.current_source = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "show_context" not in st.session_state:
    st.session_state.show_context = False

# Header with better icon
st.markdown('<div class="main-header">🩺 MedGPT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Evidence-based clinical knowledge assistant</div>', unsafe_allow_html=True)
st.markdown("---")

# Layout
left, right = st.columns([1, 1], gap="large")

# LEFT - Chat
with left:
    st.subheader("💬 Ask a question")
    
    query = st.text_input(
        "Question",
        placeholder="e.g., What are the treatment options for acute MI?",
        label_visibility="collapsed",
        key="main_query",
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_btn = st.button("🔍 Search", type="primary", use_container_width=True)
    with col2:
        context_btn = st.button("📚 Context", use_container_width=True)
    with col3:
        clear_btn = st.button("Clear", use_container_width=True)
    
    if context_btn:
        st.session_state.show_context = not st.session_state.show_context
    
    if clear_btn:
        st.session_state.chat_history = []
        st.session_state.current_source = None
        st.session_state.show_context = False
        st.rerun()
    
    if search_btn and query:
        with st.spinner("🔎 Searching..."):
            try:
                t0 = time.perf_counter()
                vs, retriever = get_retriever()
                docs = retriever.invoke(query)
                t1 = time.perf_counter()
                
                if not docs:
                    st.warning("No relevant information found")
                    st.stop()
                
                combined_context = "\n\n".join([
                    f"[Source: {d.metadata.get('source', 'Unknown')} - Page {d.metadata.get('page', 0) + 1}]\n{d.page_content}"
                    for d in docs
                ])
                
                if st.session_state.show_context:
                    with st.expander("🔍 Retrieved Context", expanded=True):
                        for i, d in enumerate(docs):
                            st.markdown(f"**Source {i+1}:** {d.metadata.get('source', 'Unknown')}")
                            st.text_area(f"Context {i+1}", d.page_content, height=120, key=f"ctx_{i}")
                
                handler = get_llm_handler()
                with st.spinner("🧠 Generating..."):
                    answer = handler.generate_answer(query, combined_context)
                
                t2 = time.perf_counter()
                
                # Store - DON'T show warning if answer is good
                st.session_state.chat_history.insert(0, {
                    "query": query,
                    "answer": answer,
                    "sources": docs,
                    "retrieval_time": t1 - t0,
                    "generation_time": t2 - t1,
                    "backend": handler.backend
                })
                st.session_state.current_source = docs[0] if docs else None
                st.session_state.current_page = docs[0].metadata.get('page', 0) if docs else 0
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # History
    st.markdown("---")
    st.subheader("📋 Recent queries")
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💭</div>
            <p>No queries yet</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, chat in enumerate(st.session_state.chat_history[:10]):
            st.markdown(f'<div class="query-bubble">{chat["query"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="response-bubble">{chat["answer"]}</div>', unsafe_allow_html=True)
            
            if chat.get("sources"):
                st.markdown("**📚 Sources:**")
                for i, src in enumerate(chat["sources"][:3]):
                    name = src.metadata.get("source", "Unknown")
                    page = src.metadata.get("page", 0)
                    if st.button(f"📄 {name} (Page {page + 1})", key=f"src_{idx}_{i}", use_container_width=True):
                        st.session_state.current_source = src
                        st.session_state.current_page = page
                        st.rerun()
            
            # Only show timing if Groq worked (fast)
            if chat.get("retrieval_time") and chat.get("backend") != "fallback":
                st.markdown(
                    f'<div class="timing-info">⏱️ {chat["retrieval_time"]:.2f}s + {chat["generation_time"]:.2f}s</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown("---")

# RIGHT - Document Viewer
with right:
    st.subheader("📖 Document viewer")
    
    src = st.session_state.current_source
    
    if src:
        name = src.metadata.get("source", "Unknown")
        page = st.session_state.current_page
        file_path = src.metadata.get("file_path", "")
        content = src.page_content or ""
        
        st.markdown(f'<div class="pdf-viewer-container"><div class="pdf-header">📄 {name}</div></div>', unsafe_allow_html=True)
        
        with st.expander("💡 Relevant excerpt", expanded=True):
            st.markdown(f'<div class="highlight-box">{content}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if file_path and Path(file_path).exists() and file_path.lower().endswith(".pdf"):
            display_pdf_page_scrollable(file_path, page, content[:120])
        else:
            st.info("📄 PDF preview not available - file path not found")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📚</div>
            <h4>No document selected</h4>
            <p>Click a source to view</p>
        </div>
        """, unsafe_allow_html=True)

# SIDEBAR - FIXED: No more "fallback" display
with st.sidebar:
    st.markdown("## 📤 Upload Files")
    render_upload_ui()
    
    st.markdown("---")
    
    st.markdown("### ⚙️ System")
    
    handler = get_llm_handler()
    status = handler.get_status()
    
    backend = status.get("backend", "unknown")
    model_name = status.get("model", "Unknown")
    
    # FIXED: Better status display without "fallback" confusion
    if backend == "groq":
        st.success(f"✓ **Groq API**")
        st.caption(f"Model: {model_name}")
    elif backend == "ollama":
        st.info(f"✓ **Ollama Local**")
        st.caption(f"Model: {model_name}")
    elif backend == "openai":
        st.success(f"✓ **OpenAI API**")
        st.caption(f"Model: {model_name}")
    else:
        # If truly fallback/offline mode
        st.warning(f"⚠️ **Limited Mode**")
        st.caption("Using basic responses")
        st.caption("Check your API keys for full functionality")
    
    st.markdown("---")
    
    st.markdown("### 📊 Knowledge")
    
    try:
        vs = load_vectorstore()
        st.metric("Chunks", f"{vs.index.ntotal:,}")
        st.caption("✅ Ready")
    except:
        st.error("Not loaded")
    
    st.markdown("---")
    
    with st.expander("ℹ️ About"):
        st.markdown("""
        **MedGPT** - Evidence-based clinical knowledge assistant
        
        Features:
        - Semantic search
        - Source citations
        - PDF viewer
        - File uploads
        
        ⚠️ Educational use only
        """)