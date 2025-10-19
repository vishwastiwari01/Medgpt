import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class DocumentProcessor:
    """Document processor with page number tracking"""
    
    def __init__(self, chunk_size=600, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, file_path: str, source_name: str, max_pages: Optional[Tuple[int, int]] = None) -> List[Dict]:
        """Process file with page tracking"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.txt':
            text = self._read_txt(file_path)
            chunks = self._create_chunks(text, source_name)
        elif ext == '.pdf':
            # Get text with page markers
            pages_data = self._read_pdf_with_pages(file_path, max_pages)
            chunks = self._create_chunks_with_pages(pages_data, source_name)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return chunks
    
    def _read_txt(self, file_path: str) -> str:
        """Read text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _read_pdf_with_pages(self, file_path: str, max_pages: Optional[Tuple[int, int]] = None) -> List[Dict]:
        """
        Read PDF and track which page each text came from
        
        Returns: List of {page_num: int, text: str}
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            
            print(f"📖 PDF has {total_pages} pages")
            
            # Determine range
            if max_pages:
                start_page, end_page = max_pages
                start_page = max(1, start_page) - 1
                end_page = min(end_page, total_pages)
                print(f"⚙️ Processing pages {start_page + 1} to {end_page}")
            else:
                start_page = 0
                end_page = total_pages
                print(f"⚠️ Processing ALL {total_pages} pages")
            
            pages_data = []
            pages_processed = 0
            
            for page_num in range(start_page, end_page):
                try:
                    page_text = reader.pages[page_num].extract_text()
                    
                    # Skip pages with very little text
                    if len(page_text.strip()) < 50:
                        continue
                    
                    # Clean the text
                    cleaned_text = self._clean_text(page_text)
                    
                    pages_data.append({
                        'page_num': page_num + 1,  # Human-readable page number
                        'text': cleaned_text
                    })
                    
                    pages_processed += 1
                    
                    # Progress
                    if pages_processed % 100 == 0:
                        print(f"  ✓ Processed {pages_processed} pages...")
                
                except Exception as e:
                    print(f"  ⚠️ Skipped page {page_num + 1}: {str(e)}")
                    continue
            
            print(f"✅ Extracted text from {pages_processed} pages with page tracking")
            return pages_data
            
        except ImportError:
            raise Exception("PyPDF2 not installed. Run: pip install PyPDF2")
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove standalone page numbers
        text = re.sub(r'\b\d{1,4}\b(?=\s|$)', '', text)
        
        # Keep medical notation
        text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\%\+\/\<\>\=\'\"\°\μ\α\β\γ]', '', text)
        
        return text.strip()
    
    def _create_chunks(self, text: str, source_name: str) -> List[Dict]:
        """Create chunks without page tracking (for TXT files)"""
        chunks = []
        words = text.split()
        
        if len(words) == 0:
            return chunks
        
        print(f"📝 Creating chunks from {len(words)} words...")
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text) < 100:
                continue
            
            chunks.append({
                'text': chunk_text,
                'source': source_name,
                'chunk_id': len(chunks)
            })
        
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    def _create_chunks_with_pages(self, pages_data: List[Dict], source_name: str) -> List[Dict]:
        """
        Create chunks from pages while tracking page numbers
        """
        chunks = []
        
        print(f"📝 Creating chunks with page tracking...")
        
        # Combine consecutive pages into chunks
        current_chunk = ""
        current_pages = []
        word_count = 0
        
        for page_data in pages_data:
            page_num = page_data['page_num']
            page_text = page_data['text']
            page_words = page_text.split()
            
            # Add to current chunk
            current_chunk += " " + page_text
            current_pages.append(page_num)
            word_count += len(page_words)
            
            # If chunk is large enough, save it
            if word_count >= self.chunk_size:
                chunk_text = current_chunk.strip()
                
                if len(chunk_text) >= 100:
                    # Determine primary page (first page in range)
                    primary_page = min(current_pages)
                    page_range = f"{min(current_pages)}-{max(current_pages)}" if len(current_pages) > 1 else str(primary_page)
                    
                    chunks.append({
                        'text': chunk_text,
                        'source': source_name,
                        'chunk_id': len(chunks),
                        'page': primary_page,
                        'page_range': page_range
                    })
                
                # Start new chunk with overlap
                overlap_words = ' '.join(chunk_text.split()[-self.chunk_overlap:])
                current_chunk = overlap_words
                current_pages = [page_num]
                word_count = len(overlap_words.split())
        
        # Add final chunk
        if len(current_chunk.strip()) >= 100:
            primary_page = min(current_pages)
            page_range = f"{min(current_pages)}-{max(current_pages)}" if len(current_pages) > 1 else str(primary_page)
            
            chunks.append({
                'text': current_chunk.strip(),
                'source': source_name,
                'chunk_id': len(chunks),
                'page': primary_page,
                'page_range': page_range
            })
        
        print(f"✅ Created {len(chunks)} chunks with page numbers")
        return chunks