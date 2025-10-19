import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

class VectorStore:
    """Simple vector store using TF-IDF (no complex dependencies)"""
    
    def __init__(self):
        """Initialize with TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.vectors = None
        self.documents = []
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        self.documents = documents
        
        # Extract texts
        texts = [doc['text'] for doc in documents]
        
        # Create TF-IDF vectors
        self.vectors = self.vectorizer.fit_transform(texts)
        
        print(f"✅ Added {len(documents)} documents to vector store")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for most relevant documents using TF-IDF similarity"""
        if self.vectors is None:
            raise ValueError("No documents in vector store. Call add_documents first.")
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        # Format results
        results = []
        for idx in top_indices:
            if idx < len(self.documents):
                result = self.documents[idx].copy()
                result['score'] = float(similarities[idx])
                results.append(result)
        
        return results