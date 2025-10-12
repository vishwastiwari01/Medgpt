"""
Medical RAG Assistant - Main Application
Run with: streamlit run app.py
"""

import os
import time
import threading
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "utils"))
from utils.llm_handler import LLMHandler

import streamlit as st
import fitz  # PyMuPDF

# === LangChain imports (new packages with graceful fallback) ===
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings  # fallback

from langchain_community.vectorstores import FAISS

# === Local LLM handler (fast, HTTP, with fallback) ===
from llm_handler import LLMHandler

# ---------- Constants ----------
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # must match preprocessing
VECTORSTORE_DIR = "vectorstore"
TOP_K = 1
RETRIEVAL_TIMEOUT_S = 120.0   # hard timeout for retrieval step
LLM_TIMEOUT_S = 120.0        # llm_handler has 30s HTTP timeout; we also guard the call

# ---------- Page config ----------
st.set_page_config(
    page_title="Medical RAG Assistant",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded",
)

# ---------- Styles ----------
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem; font-weight: 700;
        background: linear-gradient(120deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem; padding: 1rem;
    }
    .subtitle { text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem; }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 1rem 1.5rem; border-radius: 20px 20px 5px 20px;
        margin: 1rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .assistant-message {
        background: #f8f9fa; border-left: 4px solid #1f77b4; padding: 1.2rem 1.5rem;
        border-radius: 5px 20px 20px 20px; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        line-height: 1.6;
    }
    .doc-viewer-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 1rem; border-radius: 10px 10px 0 0; font-weight: 600; text-align: center;
    }
    .doc-viewer-content { background: white; border: 2px solid #e0e0e0; border-radius: 0 0 10px 10px; padding: 1.5rem; min-height: 400px; }
    .highlight-text {
        background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
        padding: 0.8rem; border-radius: 8px; border-left: 4px solid #ff6b6b; margin: 1rem 0; line-height: 1.8; font-size: 0.95rem;
        word-wrap: break-word; white-space: pre-wrap;
    }
    .empty-state { text-align: center; padding: 3rem; color: #999; }
    .empty-state-icon { font-size: 4rem; margin-bottom: 1rem; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: 600; padding: 0.6rem 1rem; transition: all 0.3s ease; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Small helpers ----------
def _run_with_timeout(fn, timeout_s, *args, **kwargs):
    """Run callable in background thread and return (result, error) or (None, TimeoutError)."""
    box = {"out": None, "err": None}
    def _target():
        try:
            box["out"] = fn(*args, **kwargs)
        except Exception as e:
            box["err"] = e
    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        return None, TimeoutError(f"Operation exceeded {timeout_s} seconds")
    return box["out"], box["err"]

# ---------- Caches ----------
@st.cache_resource(show_spinner=False)
def load_vectorstore():
    """Load pre-processed FAISS store."""
    path = Path(VECTORSTORE_DIR)
    if not path.exists():
        st.error("❌ Vectorstore not found! Run: `python preprocess_documents.py`")
        st.stop()
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vs = FAISS.load_local(str(path), embeddings, allow_dangerous_deserialization=True)
    return vs

@st.cache_resource(show_spinner=False)
def get_retriever():
    vs = load_vectorstore()
    return vs, vs.as_retriever(search_kwargs={"k": TOP_K})

@st.cache_resource(show_spinner=False)
def get_llm_handler():
    # One LLMHandler for the session (detects Ollama/Claude/fallback once)
    return LLMHandler()

# ---------- PDF rendering ----------
def display_pdf_page(pdf_path, page_num, highlight_text=None):
    doc = None
    try:
        doc = fitz.open(pdf_path)
        if not isinstance(page_num, int) or not (0 <= page_num < len(doc)):
            page_num = 0
        page = doc[page_num]

        if highlight_text:
            search_text = highlight_text[:120].strip()
            if search_text:
                try:
                    for inst in page.search_for(search_text)[:3]:
                        page.add_highlight_annot(inst)
                except Exception:
                    pass

        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
        st.image(pix.tobytes("png"), use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")
    finally:
        if doc is not None:
            doc.close()

# ---------- Session state ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_source" not in st.session_state:
    st.session_state.current_source = None

# ---------- Header ----------
st.markdown('<div class="main-header">🏥 Medical RAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Powered by local Ollama • Context-Aware Medical Q&A</div>', unsafe_allow_html=True)
st.markdown("---")

# ---------- Layout ----------
col1, col2 = st.columns([1, 1], gap="large")

# ---------- LEFT: chat ----------
with col1:
    st.markdown("### 💬 Ask a Medical Question")

    query = st.text_input(
        "Type your question here:",
        placeholder="e.g., What are the symptoms of diabetes?",
        key="query_input",
        label_visibility="collapsed",
    )

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        search_btn = st.button("🔍 Search Documents", type="primary", use_container_width=True)
    with col_btn2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.chat_history = []
        st.session_state.current_source = None
        st.rerun()

    if search_btn and query:
        status = st.status("🔎 Searching medical documents...", state="running")
        try:
            t0 = time.perf_counter()
            # Load vectorstore + retriever
            vs, retriever = get_retriever()
            t1 = time.perf_counter()
            status.update(label=f"📚 Index loaded in {t1 - t0:.2f}s… retrieving top match")

            # Retrieval with timeout guard
            docs, err = _run_with_timeout(retriever.get_relevant_documents, RETRIEVAL_TIMEOUT_S, query)
            t2 = time.perf_counter()

            if err is not None:
                status.update(label=f"⚠️ Retrieval error: {err}", state="error")
                st.stop()

            if not docs:
                status.update(label=f"ℹ️ No matching chunks (index {t1-t0:.2f}s, retrieve {t2-t1:.2f}s).", state="complete")
                st.warning("No relevant context found in your documents.")
                st.session_state.chat_history.insert(0, {
                    "query": query,
                    "answer": "I couldn’t find relevant context in the indexed documents.",
                    "source": None
                })
                st.rerun()

            # Context preview
            top = docs[0]
            context = top.page_content
            source_doc = top
            src_name = top.metadata.get("source", "Unknown")
            st.caption(f"✅ Retrieved 1 chunk in {t2-t1:.2f}s from **{src_name}**")
            with st.expander("🔎 Retrieved context preview", expanded=False):
                st.write(context[:600])

            # LLM answer via handler
            status.update(label="🤖 Generating answer (LLM)…")
            handler = get_llm_handler()

            def _answer():
                return handler.generate_answer(query, context)

            answer, aerr = _run_with_timeout(_answer, LLM_TIMEOUT_S)
            t3 = time.perf_counter()

            if aerr is not None:
                status.update(label=f"⚠️ LLM error: {aerr}", state="error")
                st.stop()

            if answer is None or not str(answer).strip():
                status.update(label=f"⏱️ LLM exceeded {LLM_TIMEOUT_S}s (index {t1-t0:.2f}s • retrieve {t2-t1:.2f}s).", state="complete")
                st.warning("The model took too long to respond. Please try again.")
                st.stop()

            st.caption(f"🤖 Answer generated in {t3 - t2:.2f}s using {handler.backend.upper()} → {handler.ollama_model or 'fallback'}")

            st.session_state.chat_history.insert(0, {
                "query": query,
                "answer": answer.strip(),
                "source": source_doc
            })
            st.session_state.current_source = source_doc

            status.update(label=f"✅ Done (index {t1-t0:.2f}s • retrieve {t2-t1:.2f}s • LLM {t3-t2:.2f}s)", state="complete")
            st.rerun()

        except Exception as e:
            status.update(label="❌ Error during search", state="error")
            st.error(f"{e}")

    # Conversation history
    st.markdown("---")
    st.markdown("### 📝 Conversation History")
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💭</div>
            <p>No questions yet. Start by asking something!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, chat in enumerate(st.session_state.chat_history[:5]):
            st.markdown(f"<div class='user-message'><strong>Q:</strong> {chat['query']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='assistant-message'>{chat['answer']}</div>", unsafe_allow_html=True)

            if chat["source"]:
                src = chat["source"]
                name = src.metadata.get("source", "Unknown")
                page = src.metadata.get("page", 0)
                if st.button(f"📄 View Source: {name} (Page {page + 1 if isinstance(page, int) else page})",
                             key=f"src_{idx}", use_container_width=True):
                    st.session_state.current_source = src
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

# ---------- RIGHT: document viewer ----------
with col2:
    st.markdown("### 📖 Document Viewer")
    if st.session_state.current_source:
        src = st.session_state.current_source
        name = src.metadata.get("source", "Unknown")
        page = src.metadata.get("page", 0)
        file_path = src.metadata.get("file_path") or src.metadata.get("source", "")
        content = src.page_content or ""

        st.markdown(f"<div class='doc-viewer-header'>📄 {name} • Page {page + 1 if isinstance(page, int) else page}</div>", unsafe_allow_html=True)

        with st.expander("📝 Relevant Text Excerpt", expanded=True):
            st.markdown(f"<div class='highlight-text'>{content}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📄 Full Document Page")
        if file_path and Path(file_path).exists():
            if file_path.lower().endswith(".pdf"):
                display_pdf_page(file_path, page if isinstance(page, int) else 0, content[:120])
            else:
                st.info("📄 Full preview available only for PDF files")
                st.text_area("Document Content", content, height=400)
        else:
            st.warning("⚠️ Source document not found")
    else:
        st.markdown("""
        <div class="doc-viewer-content">
            <div class="empty-state">
                <div class="empty-state-icon">📚</div>
                <h3>No Document Selected</h3>
                <p>Ask a question on the left to see relevant documents here</p>
            </div>
            <div class="info-box">
                <h4>📌 How It Works:</h4>
                <ol>
                    <li><strong>Ask a question</strong> using natural language</li>
                    <li><strong>Get concise answers</strong> from medical documents</li>
                    <li><strong>View source documents</strong> with highlighted relevant sections</li>
                    <li><strong>Click on sources</strong> to see the full context</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ℹ️ System Information")
    try:
        vs = load_vectorstore()
        st.success("✅ Knowledge Base Loaded")
        try:
            total = getattr(vs.index, "ntotal", None)
            if total is None:
                total = vs.index.ntotal
            st.markdown("### 📊 Statistics")
            st.metric("Total Chunks", f"{int(total):,}")
        except Exception:
            pass
    except Exception:
        st.error("❌ Knowledge Base Not Found")
        st.info("Run: `python preprocess_documents.py`")

    st.markdown("---")
    handler = get_llm_handler()
    st.markdown("### 🤖 LLM Backend")
    st.info(f"**Backend:** {handler.backend.upper()}  \n**Model:** {handler.ollama_model or '—'}")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    st.markdown(f"""
    - **Top Results:** {TOP_K}
    - **Embedding Model:** `{EMBED_MODEL}`
    - **Retrieval Timeout:** {RETRIEVAL_TIMEOUT_S}s
    - **LLM Timeout:** {LLM_TIMEOUT_S}s
    """)

    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;'>
        <p><strong>Medical RAG Assistant</strong></p>
        <p>Built with Streamlit • FAISS • Ollama</p>
        <p>⚠️ For educational purposes only</p>
    </div>
    """, unsafe_allow_html=True)
