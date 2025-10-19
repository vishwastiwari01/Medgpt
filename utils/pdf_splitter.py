"""
PDF Splitter - Automatically splits large PDFs for better processing
Handles Harrison's and other large medical textbooks
"""
from PyPDF2 import PdfReader, PdfWriter
import os
from pathlib import Path

def split_large_pdf(pdf_path, output_dir="documents/split_pdfs", max_pages=200):
    """
    Split large PDF into smaller chunks for better RAG performance
    
    Args:
        pdf_path: Path to the large PDF
        output_dir: Where to save split PDFs
        max_pages: Maximum pages per chunk
    
    Returns:
        List of paths to split PDFs
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = Path(pdf_path)
    
    try:
        reader = PdfReader(str(pdf_path))
        total_pages = len(reader.pages)
        
        print(f"📚 Processing: {pdf_path.name}")
        print(f"   Total pages: {total_pages}")
        
        if total_pages <= max_pages:
            print(f"   ✅ PDF is small enough, no splitting needed")
            return [str(pdf_path)]
        
        num_parts = (total_pages // max_pages) + (1 if total_pages % max_pages else 0)
        print(f"   📄 Splitting into {num_parts} parts...")
        
        split_files = []
        
        for i in range(num_parts):
            writer = PdfWriter()
            start_page = i * max_pages
            end_page = min(start_page + max_pages, total_pages)
            
            # Add pages to this chunk
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # Generate output filename
            base_name = pdf_path.stem
            output_path = output_dir / f"{base_name}_part{i+1}_pages{start_page+1}-{end_page}.pdf"
            
            # Write the chunk
            with open(output_path, "wb") as f:
                writer.write(f)
            
            split_files.append(str(output_path))
            print(f"   ✓ Created: {output_path.name} ({end_page - start_page} pages)")
        
        print(f"   ✅ Split complete! Created {len(split_files)} files")
        return split_files
        
    except Exception as e:
        print(f"   ❌ Error splitting PDF: {e}")
        return [str(pdf_path)]  # Return original if splitting fails


def split_all_large_pdfs(documents_dir="documents", max_pages=200):
    """
    Automatically find and split all large PDFs in documents folder
    """
    docs_path = Path(documents_dir)
    
    if not docs_path.exists():
        print(f"❌ Documents folder not found: {docs_path}")
        return []
    
    # Find all PDFs
    pdf_files = list(docs_path.glob("*.pdf"))
    
    if not pdf_files:
        print("ℹ️  No PDFs found to split")
        return []
    
    print(f"\n{'='*60}")
    print(f"📚 PDF Splitting Tool")
    print(f"{'='*60}\n")
    print(f"Found {len(pdf_files)} PDF(s) in {documents_dir}/")
    print(f"Max pages per chunk: {max_pages}\n")
    
    all_split_files = []
    large_pdfs = 0
    
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(str(pdf_file))
            total_pages = len(reader.pages)
            
            if total_pages > max_pages:
                large_pdfs += 1
                split_files = split_large_pdf(pdf_file, max_pages=max_pages)
                all_split_files.extend(split_files)
            else:
                print(f"✓ {pdf_file.name}: {total_pages} pages (no split needed)")
        except Exception as e:
            print(f"⚠️  Error reading {pdf_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Splitting Complete!")
    print(f"{'='*60}")
    print(f"Large PDFs split: {large_pdfs}")
    print(f"Total output files: {len(all_split_files)}")
    
    if all_split_files:
        print(f"\n💡 Split PDFs saved to: documents/split_pdfs/")
        print(f"   Add this folder to your preprocessing!")
    
    return all_split_files


if __name__ == "__main__":
    # Run as standalone script
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        split_large_pdf(pdf_path)
    else:
        # Split all large PDFs in documents folder
        split_all_large_pdfs()
