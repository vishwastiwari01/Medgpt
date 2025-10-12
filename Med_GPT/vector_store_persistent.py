import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from pathlib import Path

class VectorStore:
    def __init__(self, cache_path="vector_cache"):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.documents = []
        self.vectors = None
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(exist_ok=True)
        
    def add_documents(self, documents):
        """Add documents and create vectors"""
        self.documents = documents
        texts = [doc['text'] for doc in documents]
        self.vectors = self.vectorizer.fit_transform(texts)
        
    def search(self, query, k=5):
        """Search for most relevant documents"""
        if self.vectors is None:
            return []
            
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            result = self.documents[idx].copy()
            result['score'] = float(similarities[idx])
            results.append(result)
            
        return results
    
    def save(self, name="default"):
        """Save vector store to disk"""
        cache_file = self.cache_path / f"{name}.pkl"
        
        cache_data = {
            'documents': self.documents,
            'vectorizer': self.vectorizer,
            'vectors': self.vectors
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"✅ Vector store saved to {cache_file}")
        return cache_file
    
    def load(self, name="default"):
        """Load vector store from disk"""
        cache_file = self.cache_path / f"{name}.pkl"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.documents = cache_data['documents']
            self.vectorizer = cache_data['vectorizer']
            self.vectors = cache_data['vectors']
            
            print(f"✅ Loaded vector store from {cache_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading cache: {e}")
            return False
    
    def cache_exists(self, name="default"):
        """Check if cache file exists"""
        cache_file = self.cache_path / f"{name}.pkl"
        return cache_file.exists()