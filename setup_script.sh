#!/bin/bash

# MedGPT Enhanced - Setup Script v2.0
# Automated setup with all new features

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🩺 MedGPT: Clinical AI Tutor - Enhanced Setup         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
    PYTHON_CMD="python"
else
    print_error "Python not found!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Creating Enhanced Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p utils
print_success "Created utils/"

mkdir -p documents
print_success "Created documents/"

mkdir -p student_uploads/pdfs
mkdir -p student_uploads/images
touch student_uploads/.gitkeep
touch student_uploads/pdfs/.gitkeep
touch student_uploads/images/.gitkeep
print_success "Created student_uploads/ with subdirectories"

mkdir -p vectorstore
print_success "Created vectorstore/"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Checking Required Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

required_files=(
    "app.py"
    "requirements.txt"
    "utils/llm_handler.py"
    "utils/preprocess_documents.py"
    "utils/pdf_splitter.py"
    "utils/upload_handler.py"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    print_error "Some files are missing!"
    print_info "Please ensure all enhanced files are in place"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Installing Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "requirements.txt" ]; then
    print_info "Installing Python packages..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet --upgrade
    print_success "All dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Checking Documents"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

doc_count=$(find documents/ -type f \( -name "*.pdf" -o -name "*.txt" -o -name "*.docx" \) 2>/dev/null | wc -l)

if [ "$doc_count" -gt 0 ]; then
    print_success "Found $doc_count document(s)"
    
    print_info "Documents:"
    find documents/ -type f \( -name "*.pdf" -o -name "*.txt" -o -name "*.docx" \) -exec basename {} \; | while read file; do
        echo "   • $file"
    done
    
    echo ""
    read -p "Run enhanced preprocessing with auto-split? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Step 6: Enhanced Document Processing"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_info "Processing with auto-split for large PDFs..."
        $PYTHON_CMD utils/preprocess_documents.py
        
        if [ $? -eq 0 ]; then
            print_success "Preprocessing completed successfully!"
        else
            print_error "Preprocessing failed!"
            exit 1
        fi
    else
        print_warning "Skipped preprocessing"
        print_info "Run manually: python utils/preprocess_documents.py"
    fi
else
    print_warning "No documents found"
    print_info "Add PDFs/TXT/DOCX to documents/ folder"
    print_info "Large PDFs will be auto-split during preprocessing"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 7: Verifying Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test imports
$PYTHON_CMD -c "
import streamlit
import langchain
import faiss
import fitz
from PIL import Image
print('All imports successful!')
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "All Python packages verified"
else
    print_error "Some packages failed to import"
    print_info "Try: pip install -r requirements.txt --upgrade"
fi

# Check vectorstore
if [ -d "vectorstore" ] && [ "$(ls -A vectorstore)" ]; then
    if [ -f "vectorstore/index.faiss" ]; then
        print_success "Vectorstore ready for deployment"
    else
        print_warning "Vectorstore incomplete"
    fi
else
    print_warning "Vectorstore not created yet"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           ✨ SETUP COMPLETE! ✨                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Final summary
echo "📊 Setup Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "vectorstore" ] && [ -f "vectorstore/index.faiss" ]; then
    print_success "Knowledge base: Ready"
    vectorstore_size=$(du -sh vectorstore/ 2>/dev/null | cut -f1)
    echo "   Size: $vectorstore_size"
else
    print_warning "Knowledge base: Not ready"
    echo "   Run: python utils/preprocess_documents.py"
fi

echo ""
upload_count=$(find student_uploads/ -type f 2>/dev/null | wc -l)
if [ "$upload_count" -gt 0 ]; then
    print_info "Student uploads: $upload_count file(s)"
else
    print_info "Student uploads: Empty (ready for use)"
fi

echo ""
echo "🎯 New Features Available:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ Auto-split for large PDFs (Harrison's support)"
echo "  ✨ Student file upload system"
echo "  ✨ Multi-page PDF context viewer"
echo "  ✨ Doctor persona with Meditron"
echo "  ✨ Enhanced animated UI"
echo "  ✨ Enter-to-search support"
echo ""

echo "🚀 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "vectorstore/index.faiss" ]; then
    print_info "Start the app:"
    echo ""
    echo "    streamlit run app.py"
    echo ""
    print_info "Test these features:"
    echo "  • Ask clinical questions"
    echo "  • Upload PDFs/images in sidebar"
    echo "  • Click sources for multi-page view"
    echo "  • Press Enter to search"
    echo "  • Use '📚 Context' button"
else
    print_warning "First, add documents and preprocess:"
    echo ""
    echo "  1. Add PDFs to documents/ folder"
    echo "  2. Run: python utils/preprocess_documents.py"
    echo "  3. Then: streamlit run app.py"
fi

echo ""
echo "📚 Documentation:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • UPGRADE_GUIDE.md - Complete feature documentation"
echo "  • DEPLOYMENT_CHECKLIST.md - Deploy to production"
echo "  • README.md - Basic usage"
echo ""

echo "🎓 Example Questions:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • How do you manage acute MI with ST elevation?"
echo "  • What are the diagnostic criteria for diabetes?"
echo "  • Explain the treatment for hypertensive crisis"
echo "  • What is the first-line therapy for heart failure?"
echo ""

echo "💡 Pro Tips:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • Large PDFs are automatically split during preprocessing"
echo "  • Upload personal notes/images in sidebar"
echo "  • Click any source to see multi-page context"
echo "  • Use 'Context' button to see all retrieved sources"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Ready for deployment! 🎉                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if ready for deployment
ready_for_deploy=true

if [ ! -f "vectorstore/index.faiss" ]; then
    ready_for_deploy=false
fi

if [ ! -f "utils/pdf_splitter.py" ]; then
    ready_for_deploy=false
fi

if [ "$ready_for_deploy" = true ]; then
    echo "✅ System is ready for deployment!"
    echo ""
    echo "To deploy:"
    echo "  git add ."
    echo "  git commit -m 'MedGPT Enhanced v2.0'"
    echo "  git push origin master"
    echo ""
    echo "Then deploy on Streamlit Cloud"
else
    print_warning "Some setup steps incomplete"
    print_info "Complete preprocessing before deployment"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Setup script completed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"