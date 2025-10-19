"""
Google Drive Vectorstore Loader - ZIP Method (More Reliable)
Downloads FAISS vectorstore ZIP from Google Drive on deployment
"""
import os
import gdown
import zipfile
from pathlib import Path
import streamlit as st
import shutil

def download_vectorstore_from_gdrive(
    file_id: str,
    output_dir: str = "vectorstore",
    force_download: bool = False
):
    """
    Download vectorstore ZIP from Google Drive and extract
    
    Args:
        file_id: Google Drive file ID (from sharing link of ZIP file)
        output_dir: Local directory to save vectorstore
        force_download: Force re-download even if exists
    
    Returns:
        Path to vectorstore directory
    """
    output_path = Path(output_dir)
    
    # Check if already downloaded and valid
    if output_path.exists() and not force_download:
        required_files = ['index.faiss', 'index.pkl']
        has_all_files = all((output_path / f).exists() for f in required_files)
        
        if has_all_files:
            print(f"✅ Vectorstore already exists at {output_path}")
            return str(output_path)
        else:
            print(f"⚠️ Vectorstore incomplete, re-downloading...")
            shutil.rmtree(output_path)
    
    print(f"📥 Downloading vectorstore from Google Drive...")
    print(f"   File ID: {file_id}")
    
    try:
        # Create temp directory
        temp_dir = Path("temp_vectorstore_download")
        temp_dir.mkdir(exist_ok=True)
        
        zip_path = temp_dir / "vectorstore.zip"
        
        # Download ZIP file
        url = f"https://drive.google.com/uc?id={file_id}"
        
        print("   Downloading ZIP file...")
        gdown.download(url, str(zip_path), quiet=False)
        
        # Verify download
        if not zip_path.exists():
            raise Exception("Download failed - ZIP file not found")
        
        file_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ Downloaded {file_size_mb:.2f} MB")
        
        if file_size_mb < 0.1:
            raise Exception("Downloaded file is too small - check sharing permissions")
        
        # Extract ZIP
        print("   Extracting ZIP file...")
        output_path.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Move files to correct location
        # Handle case where ZIP contains a folder or files directly
        extracted_items = list(temp_dir.iterdir())
        vectorstore_folder = None
        
        # Find the vectorstore folder in extracted items
        for item in extracted_items:
            if item.is_dir() and item.name == 'vectorstore':
                vectorstore_folder = item
                break
        
        if vectorstore_folder:
            # Move contents of vectorstore folder
            for item in vectorstore_folder.iterdir():
                dest = output_path / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
        else:
            # Files are directly in temp_dir
            for item in extracted_items:
                if item.suffix in ['.faiss', '.pkl'] or item.name in ['index.faiss', 'index.pkl']:
                    dest = output_path / item.name
                    if dest.exists():
                        dest.unlink()
                    shutil.move(str(item), str(dest))
        
        # Verify extraction
        required_files = ['index.faiss', 'index.pkl']
        missing_files = [f for f in required_files if not (output_path / f).exists()]
        
        if missing_files:
            raise Exception(f"Missing required files after extraction: {missing_files}")
        
        print(f"   ✅ Vectorstore extracted to {output_path}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return str(output_path)
        
    except Exception as e:
        error_msg = f"❌ Error downloading vectorstore: {e}"
        print(error_msg)
        
        # Show helpful error message in Streamlit
        st.error(error_msg)
        st.error("Please check:")
        st.markdown("""
        1. ✅ ZIP file is shared as "Anyone with the link"
        2. ✅ File ID is correct (from the ZIP file, not folder)
        3. ✅ ZIP contains `index.faiss` and `index.pkl`
        
        **To create the ZIP:**
```bash
        zip -r vectorstore.zip vectorstore/
```
        """)
        
        raise


def get_gdrive_file_id():
    """
    Get Google Drive file ID from environment or secrets
    
    Priority:
    1. Streamlit secrets (for deployment)
    2. Environment variable (for local testing)
    3. Hardcoded fallback
    """
    file_id = None
    source = None
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        file_id = st.secrets.get("GDRIVE_VECTORSTORE_ZIP_ID")
        if file_id:
            source = "Streamlit Secrets"
            print(f"✓ Found file ID in Streamlit Secrets")
    except Exception as e:
        print(f"⚠️ Could not read Streamlit secrets: {e}")
    
    # Try environment variable
    if not file_id:
        file_id = os.getenv("GDRIVE_VECTORSTORE_ZIP_ID")
        if file_id:
            source = "Environment Variable"
            print(f"✓ Found file ID in Environment Variable")
    
    # Hardcoded fallback (temporary for debugging)
    if not file_id:
        file_id = "1ig2qdAZEd2jcsNtBIfMquUPduhVaZSmj"  # Your ZIP file ID
        source = "Hardcoded Fallback"
        print(f"⚠️ Using hardcoded file ID (fallback)")
    
    if not file_id:
        raise ValueError(
            "Google Drive ZIP file ID not found!\n"
            "Please set GDRIVE_VECTORSTORE_ZIP_ID in:\n"
            "- Streamlit secrets (for deployment)\n"
            "- Environment variable (for local testing)\n"
            "- Or hardcode it in gdrive_loader.py"
        )
    
    print(f"Using file ID from: {source}")
    return file_id