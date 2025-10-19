# 🏗️ Medical RAG Assistant - System Architecture

## 📊 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                      (Streamlit Web App)                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ├─────────────────────────────────────┐
                               │                                     │
                      ┌────────▼─────────┐              ┌───────────▼────────┐
                      │  QUERY INTERFACE │              │  DOCUMENT VIEWER   │
                      │                  │              │                    │
                      │  • Text Input    │              │  • PDF Renderer    │
                      │  • Search Button │              │  • Highlighting    │
                      │  • Chat History  │              │  • Page Display    │
                      └────────┬─────────┘              └────────────────────┘
                               │
                               │ User Query
                               │
                      ┌────────▼──────────────────────────────────────────┐
                      │           RAG ORCHESTRATION                       │
                      │         (Langchain QA Chain)                      │
                      │                                                   │
                      │  • Query Processing                               │
                      │  • Retrieval Coordination                         │
                      │  • Answer Generation                              │
                      └────────┬──────────────────────┬───────────────────┘
                               │                      │
                    ┌──────────▼──────────┐  ┌───────▼────────────┐
                    │  VECTOR SEARCH      │  │  LLM INFERENCE     │
                    │  (FAISS Index)      │  │  (Ollama Meditron) │
                    │                     │  │                    │
                    │  • Similarity Search│  │  • Context + Query │
                    │  • Top-k Retrieval  │  │  • Answer Generate │
                    │  • k=1 (Top Result) │  │  • Temp = 0.3      │
                    └──────────┬──────────┘  └────────────────────┘
                               │
                               │ Retrieved Chunks
                               │
                      ┌────────▼─────────┐
                      │  VECTORSTORE     │
                      │  (Pre-processed) │
                      │                  │
                      │  • index.faiss   │
                      │  • index.pkl     │
                      │  • metadata.pkl  │
                      └────────┬─────────┘
                               │
                               │ Created by
                               │
                      ┌────────▼─────────────────────────────────┐
                      │     PREPROCESSING PIPELINE                │
                      │  (utils/preprocess_documents.py)          │
                      │                                           │
                      │  1. Document Loading                      │
                      │     ├─ PDF (PyPDFLoader)                 │
                      │     ├─ TXT (TextLoader)                  │
                      │     └─ DOCX (Docx2txtLoader)             │
                      │                                           │
                      │  2. Text Chunking                         │
                      │     ├─ RecursiveCharacterTextSplitter    │
                      │     ├─ chunk_size: 500                   │
                      │     └─ chunk_overlap: 50                 │
                      │                                           │
                      │  3. Embedding Generation                  │
                      │     └─ HuggingFaceEmbeddings             │
                      │        (all-MiniLM-L6-v2)                │
                      │                                           │
                      │  4. Vector Index Creation                 │
                      │     └─ FAISS.from_documents()            │
                      └───────────────────┬───────────────────────┘
                                          │
                                          │ Source Documents
                                          │
                                 ┌────────▼─────────┐
                                 │  DOCUMENTS/      │
                                 │                  │
                                 │  • *.pdf files   │
                                 │  • *.txt files   │
                                 │  • *.docx files  │
                                 └──────────────────┘
```

---

## 🔄 Request Flow Diagram

### Query Processing Flow

```
┌─────────────┐
│ User Types  │
│  Question   │
└──────┬──────┘
       │
       │ 1. Submit Query
       ▼
┌─────────────────────────────────────┐
│  Query Validation & Processing      │
│  • Check length                     │
│  • Clean input                      │
│  • Add to session state             │
└──────┬──────────────────────────────┘
       │
       │ 2. Semantic Search
       ▼
┌─────────────────────────────────────┐
│  Vector Similarity Search           │
│  • Convert query to embedding       │
│  • Search FAISS index               │
│  • Retrieve top 1 result (k=1)      │
│  • Extract source metadata          │
└──────┬──────────────────────────────┘
       │
       │ 3. Context Retrieved
       │    • Document chunk
       │    • Source file
       │    • Page number
       ▼
┌─────────────────────────────────────┐
│  LLM Inference (Ollama Meditron)    │
│  • Build prompt with context        │
│  • Generate concise answer (2-3s)   │
│  • Temperature: 0.3                 │
│  • Max tokens: auto                 │
└──────┬──────────────────────────────┘
       │
       │ 4. Answer Generated
       ▼
┌─────────────────────────────────────┐
│  Response Assembly                  │
│  • Format answer text               │
│  • Add source citation              │
│  • Create clickable button          │
│  • Prepare PDF highlight data       │
└──────┬──────────────────────────────┘
       │
       │ 5. Display to User
       ▼
┌─────────────────────────────────────┐
│  UI Update                          │
│  ├─ Left Panel: Answer + Source     │
│  └─ Right Panel: PDF with highlight │
└─────────────────────────────────────┘
```

**Typical Timeline:**
- Vector Search: ~100ms
- LLM Inference: ~3-4s
- UI Render: ~200ms
- **Total: ~3.5-5s**

---

## 🗂️ Data Flow Architecture

### One-Time Preprocessing

```
📄 Raw Documents (documents/*.pdf)
           │
           │ 1. Load
           ▼
📚 Document Objects (Langchain Documents)
           │
           │ 2. Split
           ▼
🔢 Text Chunks (500 tokens each, 50 overlap)
           │
           │ 3. Embed
           ▼
🔢 Vector Embeddings (384 dimensions)
           │
           │ 4. Index
           ▼
💾 FAISS Index (vectorstore/)
```

### Runtime Query Processing

```
💬 User Query ("What is diabetes?")
           │
           │ 1. Embed
           ▼
🔢 Query Vector (384 dimensions)
           │
           │ 2. Search
           ▼
🎯 Similar Vectors (Top 1, cosine similarity)
           │
           │ 3. Retrieve
           ▼
📄 Document Chunk + Metadata
           │
           │ 4. Combine
           ▼
📝 Prompt = Context + Query
           │
           │ 5. Generate
           ▼
💬 Answer + Source Citation
```

---

## 🏛️ Component Architecture

### 1. Frontend Layer (Streamlit)

```python
┌─────────────────────────────────────────────┐
│           Streamlit UI Components           │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │ Chat Panel   │    │  Document Viewer │  │
│  │              │    │                  │  │
│  │ • Input Box  │    │  • PDF Display   │  │
│  │ • History    │    │  • Highlights    │  │
│  │ • Sources    │    │  • Excerpts      │  │
│  └──────────────┘    └──────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │         Session State                │  │
│  │  • chat_history: List[Dict]          │  │
│  │  • current_source: Document          │  │
│  │  • qa_chain: RetrievalQA            │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### 2. RAG Layer (Langchain)

```python
┌─────────────────────────────────────────────┐
│          Langchain RAG Pipeline             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │   RetrievalQA Chain                  │  │
│  │                                      │  │
│  │   Input: {"query": "..."}           │  │
│  │   Output: {                          │  │
│  │     "result": "...",                 │  │
│  │     "source_documents": [...]        │  │
│  │   }                                  │  │
│  └──────────────────────────────────────┘  │
│                │                            │
│                ├── Retriever               │
│                │   (VectorStoreRetriever)   │
│                │                            │
│                └── LLM                      │
│                    (Ollama Meditron)        │
│                                             │
└─────────────────────────────────────────────┘
```

### 3. Vector Store Layer (FAISS)

```python
┌─────────────────────────────────────────────┐
│            FAISS Vector Store               │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Index (index.faiss)                 │  │
│  │  • 387 vectors                       │  │
│  │  • 384 dimensions                    │  │
│  │  • Cosine similarity                 │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Metadata (index.pkl)                │  │
│  │  • Document IDs                      │  │
│  │  • Mappings                          │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Chunks (chunks_metadata.pkl)        │  │
│  │  • Text content                      │  │
│  │  • Source files                      │  │
│  │  • Page numbers                      │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### 4. LLM Layer (Ollama)

```python
┌─────────────────────────────────────────────┐
│          Ollama Meditron Service            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Model: meditron (7B parameters)     │  │
│  │  Type: Medical-specialized LLM       │  │
│  │  Temperature: 0.3                    │  │
│  │  Context Window: 4096 tokens         │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Input:                                     │
│    Prompt (Context + Question)              │
│                                             │
│  Output:                                    │
│    Concise Medical Answer (2-3 sentences)   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────┐
│         Security Layers                     │
├─────────────────────────────────────────────┤
│                                             │
│  1. Input Validation                        │
│     • Query length limits                   │
│     • XSS prevention                        │
│     • SQL injection protection              │
│                                             │
│  2. File Access Control                     │
│     • Restricted to documents/ folder       │
│     • No system file access                 │
│     • Path traversal prevention             │
│                                             │
│  3. Data Privacy                            │
│     • Local processing (no external APIs)   │
│     • No data logging by default            │
│     • Session-based state                   │
│                                             │
│  4. Rate Limiting                           │
│     • Per-session query limits              │
│     • Cooldown periods                      │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📊 Performance Architecture

### Caching Strategy

```
┌─────────────────────────────────────────────┐
│          Multi-Level Caching                │
├─────────────────────────────────────────────┤
│                                             │
│  Level 1: Streamlit @cache_resource         │
│  ├─ Vectorstore (loaded once)               │
│  ├─ QA Chain (loaded once)                  │
│  └─ Embeddings Model (loaded once)          │
│                                             │
│  Level 2: Session State                     │
│  ├─ Chat history                            │
│  ├─ Current source                          │
│  └─ User preferences                        │
│                                             │
│  Level 3: FAISS Internal                    │
│  ├─ Vector index                            │
│  └─ Fast similarity search                  │
│                                             │
└─────────────────────────────────────────────┘
```

### Resource Management

```
Component              Memory    CPU      I/O
─────────────────────────────────────────────
Streamlit UI           ~50MB     Low      Low
FAISS Index           ~100MB     Low      Disk (once)
Embeddings Model      ~150MB     Med      None
Ollama Meditron      ~4-8GB     High     None
PDF Rendering          ~50MB     Med      Disk
Total                 ~4.5GB     Med      Low
```

---

## 🔄 Deployment Architecture

### Local Development

```
┌─────────────────────────────────────────┐
│      Developer Machine                  │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Streamlit (localhost:8501)       │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │  Ollama Service (localhost:11434) │ │
│  │  • Meditron Model                 │ │
│  └───────────────────────────────────┘ │
│                                         │
│  📁 Project Files                       │
│  ├─ app.py                              │
│  ├─ utils/preprocess_documents.py       │
│  ├─ documents/ (local PDFs)             │
│  └─ vectorstore/ (local FAISS)          │
│                                         │
└─────────────────────────────────────────┘
```

### Production Deployment (Docker)

```
┌──────────────────────────────────────────────────┐
│            Cloud VM (AWS/GCP/Azure)              │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │         Docker Container                   │ │
│  │  ┌──────────────────────────────────────┐ │ │
│  │  │  Streamlit App (port 8501)           │ │ │
│  │  └──────────────┬───────────────────────┘ │ │
│  │                 │                          │ │
│  │  ┌──────────────▼───────────────────────┐ │ │
│  │  │  Ollama Service                      │ │ │
│  │  │  • Meditron Model (in container)     │ │ │
│  │  └──────────────────────────────────────┘ │