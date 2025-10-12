#!/bin/bash

# Medical RAG Assistant - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Medical RAG Assistant - Automated Setup                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Step 1: Check Python version
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking Python version..."
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
    print_error "Python not found! Please install Python 3.8 or higher."
    exit 1
fi

# Step 2: Create directory structure
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Creating project structure..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p utils
print_success "Created utils/ directory"

mkdir -p documents
print_success "Created documents/ directory"

# Step 3: Check if files exist
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Checking required files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

required_files=("app.py" "requirements.txt" "utils/preprocess_documents.py")
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
    print_error "Some required files are missing. Please ensure all files are in place."
    exit 1
fi

# Step 4: Install Python dependencies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "requirements.txt" ]; then
    print_info "Installing packages (this may take a few minutes)..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet
    print_success "All Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Step 5: Check Ollama
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Checking Ollama installation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v ollama &> /dev/null; then
    print_success "Ollama is installed"
    
    # Check if Meditron model is available
    if ollama list | grep -q "meditron"; then
        print_success "Meditron model found"
    else
        print_warning "Meditron model not found"
        read -p "Do you want to pull the Meditron model now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Pulling Meditron model (this will take several minutes)..."
            ollama pull meditron
            print_success "Meditron model installed"
        else
            print_warning "You'll need to run 'ollama pull meditron' manually later"
        fi
    fi
else
    print_error "Ollama not found!"
    print_info "Please install Ollama from: https://ollama.ai"
    print_info "After installation, run: ollama pull meditron"
    exit 1
fi

# Step 6: Check documents
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Checking for documents..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

doc_count=$(find documents/ -type f \( -name "*.pdf" -o -name "*.txt" -o -name "*.docx" \) 2>/dev/null | wc -l)

if [ "$doc_count" -gt 0 ]; then
    print_success "Found $doc_count document(s) in documents/ folder"
    
    # List documents
    print_info "Documents found:"
    find documents/ -type f \( -name "*.pdf" -o -name "*.txt" -o -name "*.docx" \) -exec basename {} \; | while read file; do
        echo "   • $file"
    done
    
    # Ask to preprocess
    echo ""
    read -p "Do you want to preprocess documents now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Step 7: Preprocessing documents..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        $PYTHON_CMD utils/preprocess_documents.py
    else
        print_warning "Skipped preprocessing. Run manually: python utils/preprocess_documents.py"
    fi
else
    print_warning "No documents found in documents/ folder"
    print_info "Please add PDF, TXT, or DOCX files to documents/ folder"
    print_info "Then run: python utils/preprocess_documents.py"
fi

# Step 7: Final summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 SETUP COMPLETE! 🎉                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if vectorstore exists
if [ -d "vectorstore" ] && [ "$(ls -A vectorstore)" ]; then
    print_success "Vectorstore is ready"
    echo ""
    print_info "You can now start the application with:"
    echo ""
    echo "    streamlit run app.py"
    echo ""
else
    print_warning "Vectorstore not created yet"
    echo ""
    print_info "Before starting the app, please:"
    echo "  1. Add documents to documents/ folder"
    echo "  2. Run: python utils/preprocess_documents.py"
    echo "  3. Then run: streamlit run app.py"
    echo ""
fi

# Show project structure
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Project Structure:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tree -L 2 -I '__pycache__|*.pyc' . 2>/dev/null || ls -R

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Setup script completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"