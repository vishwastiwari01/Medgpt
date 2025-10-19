#!/bin/bash
# Quick setup script for MedGPT
# Makes it easy to configure the environment

echo "🏥 MedGPT Setup Script"
echo "======================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "Exiting without changes"
        exit 0
    fi
fi

# Get Groq API key
echo ""
echo "📝 Please enter your Groq API key"
echo "   (Get one free at: https://console.groq.com)"
read -p "GROQ_API_KEY: " groq_key

if [ -z "$groq_key" ]; then
    echo "❌ Error: API key cannot be empty"
    exit 1
fi

# Ask about model preference
echo ""
echo "🤖 Choose a model:"
echo "   1) llama-3.1-8b-instant (RECOMMENDED - Fast & Free)"
echo "   2) llama-3.3-70b-versatile (Better quality, may have limits)"
echo "   3) mixtral-8x7b-32768 (Alternative)"
read -p "Choice (1-3) [1]: " model_choice

case $model_choice in
    2)
        model="llama-3.3-70b-versatile"
        ;;
    3)
        model="mixtral-8x7b-32768"
        ;;
    *)
        model="llama-3.1-8b-instant"
        ;;
esac

# Create .env file
cat > .env << EOF
# MedGPT Configuration
# Generated: $(date)

# Groq API Configuration
GROQ_API_KEY=$groq_key
GROQ_MODEL=$model

# Optional: Ollama fallback (if you have it installed locally)
# OLLAMA_BASE_URL=http://127.0.0.1:11434

# Vector Store Configuration
# VECTORSTORE_DIR=vectorstore
# EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
EOF

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "📋 Your configuration:"
echo "   Model: $model"
echo "   API Key: ${groq_key:0:10}..."
echo ""
echo "🚀 Next steps:"
echo "   1. Test your setup:"
echo "      python test_groq_models.py"
echo ""
echo "   2. Preprocess your documents:"
echo "      python utils/preprocess_documents.py"
echo ""
echo "   3. Run MedGPT:"
echo "      streamlit run app.py"
echo ""
echo "✨ Happy learning!"
