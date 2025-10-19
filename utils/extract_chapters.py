"""
Script to extract specific chapters from Harrison's Internal Medicine
Usage: python extract_chapters.py
"""
from utils.pdf_extractor import EnhancedPDFExtractor
from pathlib import Path

def main():
    # Path to your Harrison's PDF
    harrisons_path = "harrisons_internal_medicine.pdf"  # Update this!
    
    if not Path(harrisons_path).exists():
        print(f"❌ File not found: {harrisons_path}")
        print("Please update the path to your Harrison's PDF")
        return
    
    extractor = EnhancedPDFExtractor()
    
    print("=" * 60)
    print("Harrison's Chapter Extractor")
    print("=" * 60)
    
    # Choose what to extract
    print("\nWhat would you like to extract?")
    print("1. Specific chapters (recommended)")
    print("2. First N pages (for testing)")
    print("3. Entire book (will take 20-30 minutes!)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\nEnter chapter topics (comma-separated)")
        print("Example: Diabetes Mellitus, Hypertension, Heart Failure")
        keywords_input = input("\nChapter topics: ").strip()
        keywords = [k.strip() for k in keywords_input.split(',')]
        
        print(f"\n🔍 Searching for chapters containing: {keywords}")
        text = extractor.extract_specific_chapters(harrisons_path, keywords)
        
        # Save to file
        output_file = "documents/harrisons_selected_chapters.txt"
        Path("documents").mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\n✅ Extracted {len(text)} characters")
        print(f"✅ Saved to: {output_file}")
        print(f"\nYou can now load this in MedGPT!")
    
    elif choice == "2":
        pages = int(input("\nHow many pages to extract? (e.g., 100): ").strip())
        
        print(f"\n📖 Extracting first {pages} pages...")
        text = extractor.extract_from_pdf(harrisons_path, max_pages=pages)
        
        # Clean text
        text = extractor.clean_medical_text(text)
        
        # Save to file
        output_file = f"documents/harrisons_first_{pages}_pages.txt"
        Path("documents").mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\n✅ Extracted {len(text)} characters")
        print(f"✅ Saved to: {output_file}")
    
    elif choice == "3":
        confirm = input("\n⚠️ This will take 20-30 minutes. Continue? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            print("\n📖 Extracting entire book... (this will take a while)")
            text = extractor.extract_from_pdf(harrisons_path)
            text = extractor.clean_medical_text(text)
            
            output_file = "documents/harrisons_complete.txt"
            Path("documents").mkdir(exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"\n✅ Extracted {len(text)} characters")
            print(f"✅ Saved to: {output_file}")
        else:
            print("Cancelled.")
    else:
        print("Invalid choice")
    
    print("\n" + "=" * 60)
    print("Done! Now run: python -m streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()