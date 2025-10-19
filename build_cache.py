"""
Build vector store cache for deployment
Run this once: python build_cache.py
"""
from pathlib import Path
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore

def build_cache():
    print("=" * 60)
    print("🏗️  Building Vector Store Cache for Deployment")
    print("=" * 60)
    
    # Initialize
    processor = DocumentProcessor()
    vector_store = VectorStore()
    
    # Find documents
    docs_folder = Path("documents")
    if not docs_folder.exists():
        print("❌ documents/ folder not found!")
        return
    
    all_files = list(docs_folder.glob("*.txt")) + list(docs_folder.glob("*.pdf"))
    
    if not all_files:
        print("❌ No documents found!")
        return
    
    print(f"\n📚 Found {len(all_files)} documents:")
    for f in all_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  • {f.name} ({size_mb:.2f} MB)")
    
    # Process all documents
    print("\n⚙️  Processing documents...")
    all_chunks = []
    
    for idx, file_path in enumerate(all_files, 1):
        print(f"\n[{idx}/{len(all_files)}] Processing: {file_path.name}")
        
        try:
            chunks = processor.process_file(
                str(file_path),
                file_path.name,
                max_pages=(1, 500) if file_path.suffix == '.pdf' else None
            )
            all_chunks.extend(chunks)
            print(f"  ✅ Created {len(chunks)} chunks")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if not all_chunks:
        print("\n❌ No chunks created!")
        return
    
    # Build vector store
    print(f"\n🔨 Building vector index from {len(all_chunks)} chunks...")
    vector_store.add_documents(all_chunks)
    
    # Save cache
    print("\n💾 Saving cache...")
    cache_file = vector_store.save("medical_docs")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Cache Built Successfully!")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"  • Documents: {len(all_files)}")
    print(f"  • Chunks: {len(all_chunks)}")
    print(f"  • Cache file: {cache_file}")
    print(f"  • Size: {cache_file.stat().st_size / (1024 * 1024):.2f} MB")
    
    print("\n🚀 Deployment Ready!")
    print("  1. Include 'vector_cache/' folder in deployment")
    print("  2. App will auto-load on startup")
    print("  3. No initialization needed!")
    
    print("\n💡 To test:")
    print("  python -m streamlit run app.py")
    
    return True

if __name__ == "__main__":
    build_cache()