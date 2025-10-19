"""
Enhanced PDF extraction for large medical textbooks like Harrison's
"""
from PyPDF2 import PdfReader
import re
from typing import List, Dict

class EnhancedPDFExtractor:
    """Better PDF extraction with chapter detection and filtering"""
    
    def __init__(self):
        self.min_text_length = 50  # Skip pages with too little text
    
    def extract_from_pdf(self, pdf_path: str, max_pages: int = None) -> str:
        """
        Extract text from PDF with optional page limit
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Limit extraction to first N pages (useful for testing)
        """
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            
            print(f"📖 PDF has {total_pages} pages")
            
            if max_pages:
                print(f"⚠️ Limiting to first {max_pages} pages for faster processing")
                pages_to_process = min(max_pages, total_pages)
            else:
                pages_to_process = total_pages
            
            text = ""
            processed = 0
            
            for i in range(pages_to_process):
                page_text = reader.pages[i].extract_text()
                
                # Skip if page has very little text (likely image/diagram)
                if len(page_text.strip()) < self.min_text_length:
                    continue
                
                text += page_text + "\n\n"
                processed += 1
                
                # Progress indicator
                if processed % 50 == 0:
                    print(f"  Processed {processed}/{pages_to_process} pages...")
            
            print(f"✅ Extracted text from {processed} pages")
            return text
            
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_specific_chapters(self, pdf_path: str, chapter_keywords: List[str]) -> str:
        """
        Extract only specific chapters based on keywords
        
        Example: extract_specific_chapters(pdf, ['Diabetes', 'Hypertension'])
        """
        reader = PdfReader(pdf_path)
        text = ""
        in_target_chapter = False
        
        for page in reader.pages:
            page_text = page.extract_text()
            
            # Check if this page starts a target chapter
            for keyword in chapter_keywords:
                if keyword.lower() in page_text[:200].lower():  # Check first 200 chars
                    in_target_chapter = True
                    print(f"📌 Found chapter: {keyword}")
                    break
            
            if in_target_chapter:
                text += page_text + "\n\n"
                
                # Stop if we hit a new non-target chapter
                if "CHAPTER" in page_text[:100].upper() and not any(k.lower() in page_text[:200].lower() for k in chapter_keywords):
                    in_target_chapter = False
        
        return text
    
    def clean_medical_text(self, text: str) -> str:
        """Clean extracted text for better processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers
        text = re.sub(r'\b\d{1,4}\b\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\%\+\/\<\>\'\"]', '', text)
        
        return text.strip()