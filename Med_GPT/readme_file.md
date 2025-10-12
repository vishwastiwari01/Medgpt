# 🏥 MedGPT - Evidence-Based Clinical Decision Support

A proof-of-concept AI system that provides **verifiable, citation-backed medical information** by grounding all responses in trusted medical documents.

## 🎯 Problem Statement

General-purpose AI models like ChatGPT can hallucinate medical information, making them unsafe for clinical decision support. Healthcare professionals need AI tools that:
- Only answer from verified medical sources
- Provide transparent citations
- Admit when information is unavailable
- Never hallucinate or guess

## ✨ Our Solution

MedGPT demonstrates a safer approach:
1. **Grounded Responses**: Every answer comes exclusively from uploaded medical documents
2. **Transparent Citations**: Every claim references its source document
3. **No Hallucinations**: If the knowledge base lacks information, we explicitly say so
4. **Verifiable**: Users can check original sources for any claim

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone or download this repository
cd medgpt-demo

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Optional: Add Claude API Key

For full AI-generated responses, add your Anthropic API key:

1. Create a `.env` file in the project root
2. Add: `ANTHROPIC_API_KEY=your_key_here`
3. Get your key from: https://console.anthropic.com/

Without an API key, the system still works with simplified responses.

## 📖 How to Use

1. **Load Documents**: 
   - Click "Use Sample Medical Documents" in the sidebar
   - Or upload your own medical PDFs/TXT files

2. **Initialize**: Click "Initialize Sample Documents" or "Process Documents"

3. **Ask Questions**: Type clinical questions like:
   - "What is the first-line treatment for Type 2 Diabetes?"
   - "What are the diagnostic criteria for hypertension?"
   - "What antibiotics are used for community-acquired pneumonia?"

4. **Review Answers**: Each answer includes:
   - Evidence-based response
   - Source citations
   - Expandable section showing original document excerpts

## 🏗️ System Architecture

```
User Question
     ↓
Document Processing (chunks documents)
     ↓
Vector Embeddings (sentence-transformers)
     ↓
Semantic Search (FAISS)
     ↓
Context Retrieval (top 5 relevant chunks)
     ↓
LLM Generation (Claude with strict prompt)
     ↓
Cited Answer
```

## 📦 Tech Stack

- **Frontend**: Streamlit
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: FAISS
- **LLM**: Claude Sonnet 4.5 (optional)
- **Document Processing**: PyPDF2

## 📁 Project Structure

```
medgpt-demo/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── documents/                  # Sample medical documents
│   ├── diabetes_guidelines.txt
│   ├── hypertension_management.txt
│   └── antibiotic_protocols.txt
├── utils/
│   ├── document_processor.py   # Text extraction & chunking
│   ├── vector_store.py         # Embedding & search
│   └── llm_handler.py          # LLM API integration
└── README.md
```

## 🎓 Sample Queries to Try

1. "What is the first-line medication for type 2 diabetes?"
2. "What are the blood pressure targets for hypertension treatment?"
3. "Which antibiotic should I use for streptococcal pharyngitis?"
4. "What are the diagnostic criteria for diabetes?"
5. "How do you manage resistant hypertension?"

## 🔮 Future Vision

This demo uses 3 documents with ~100 chunks. The full vision includes:

- **Expanded Knowledge Base**: Medical textbooks, clinical guidelines, research papers
- **Specialty Modules**: Cardiology, Oncology, Pediatrics, etc.
- **Real-time Updates**: Latest clinical trials and guidelines
- **Multi-modal**: Images, lab results, ECGs
- **Clinical Workflow Integration**: EMR integration, order sets
- **Audit Trail**: Complete tracking of AI decision support

## ⚠️ Important Disclaimers

- **Not for Clinical Use**: This is a demonstration system for educational purposes
- **Always Verify**: Consult appropriate medical professionals for patient care decisions
- **Demo Limitations**: Uses limited sample documents, not comprehensive medical knowledge
- **No Medical Advice**: System provides information synthesis, not clinical recommendations

## 🤝 Contributing

This is a buildathon proof-of-concept. Suggestions for improvement:
- Add more medical documents
- Improve chunking strategies
- Enhance citation formatting
- Add document upload validation
- Implement feedback mechanisms

## 📄 License

Educational/Demo purposes. Not licensed for clinical use.

## 👥 Team

Built for [Your Buildathon Name] to demonstrate safer AI in healthcare.

## 📧 Contact

[Your Contact Information]

---

**Remember**: This system shows what's possible when AI is grounded in verified sources. Every answer is verifiable. Every claim is cited. Zero hallucinations.