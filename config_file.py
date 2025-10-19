"""
Configuration file for MedGPT
"""

# Document Processing Settings
CHUNK_SIZE = 500  # Number of words per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks

# Vector Store Settings
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Lightweight model (23MB)
VECTOR_SEARCH_K = 5  # Number of results to retrieve

# LLM Settings
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE = 0.1  # Low temperature for factual responses

# App Settings
APP_TITLE = "MedGPT - Evidence-Based Clinical Support"
APP_ICON = "🏥"

# Paths
DOCUMENTS_FOLDER = "documents"
CACHE_FOLDER = ".cache"