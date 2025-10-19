"""
Google Drive Vectorstore Loader
Downloads FAISS vectorstore from Google Drive on deployment
"""
import os
import gdown
import zipfile
from pathlib import Path
import streamlit as st

def download_vectorstore_from_gdrive(
    folder_id: str,
    output_dir: str = "vectorstore",
    force_download: bool = False
):
    """
    Download vectorstore from Google Drive
    
    Args:
        folder_id: Google Drive folder ID (from sharing link)
        output_dir: Local directory to save vectorstore
        force_download: Force re-download even if exists
    
    Returns:
        Path to vectorstore directory
    """
    output_path = Path(output_dir)
    
    # Check if already downloaded
    if output_path.exists() and not force_download:
        # Verify it has the required FAISS files
        required_files = ['index.faiss', 'index.pkl']
        has_all_files = all((output_path / f).exists() for f in required_files)
        
        if has_all_files:
            print(f"✅ Vectorstore already exists at {output_path}")
            return str(output_path)
    
    print(f"📥 Downloading vectorstore from Google Drive...")
    print(f"   Folder ID: {folder_id}")
    
    try:
        # Create temp directory
        temp_dir = Path("temp_download")
        temp_dir.mkdir(exist_ok=True)
        
        # Download as zip (easier than folder download)
        zip_path = temp_dir / "vectorstore.zip"
        
        # Google Drive folder download URL
        url = f"https://drive.google.com/uc?id={folder_id}"
        
        # Try to download
        print("   Downloading...")
        gdown.download(url, str(zip_path), quiet=False, fuzzy=True)
        
        # If that didn't work, try folder download
        if not zip_path.exists() or zip_path.stat().st_size < 1000:
            print("   Trying alternative download method...")
            gdown.download_folder(
                id=folder_id,
                output=str(temp_dir / "vectorstore"),
                quiet=False
            )
            
            # Move files to output directory
            output_path.mkdir(parents=True, exist_ok=True)
            src_dir = temp_dir / "vectorstore"
            
            if src_dir.exists():
                for item in src_dir.iterdir():
                    dest = output_path / item.name
                    if item.is_file():
                        item.replace(dest)
                print(f"   ✅ Vectorstore downloaded to {output_path}")
                return str(output_path)
        
        # Extract zip if we downloaded one
        if zip_path.exists() and zip_path.stat().st_size > 1000:
            print("   Extracting...")
            output_path.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_path)
            
            print(f"   ✅ Vectorstore extracted to {output_path}")
            
            # Cleanup
            zip_path.unlink()
            
            return str(output_path)
        
        raise Exception("Download failed - file too small or not found")
        
    except Exception as e:
        error_msg = f"❌ Error downloading vectorstore: {e}"
        print(error_msg)
        
        # Show helpful error message
        st.error(error_msg)
        st.error("Please check:")
        st.markdown("""
        1. ✅ Folder is shared as "Anyone with the link"
        2. ✅ Folder ID is correct
        3. ✅ Folder contains `index.faiss` and `index.pkl`
        """)
        
        raise


def get_gdrive_folder_id():
    """
    Get Google Drive folder ID from environment or secrets
    
    Priority:
    1. Streamlit secrets (for deployment)
    2. Environment variable (for local testing)
    3. Hardcoded fallback
    """
    # Try Streamlit secrets first (for cloud deployment)
    try:
        folder_id = st.secrets.get("GDRIVE_VECTORSTORE_ID")
        if folder_id:
            return folder_id
    except:
        pass
    
    # Try environment variable
    folder_id = os.getenv("GDRIVE_VECTORSTORE_ID")
    if folder_id:
        return folder_id
    
    # Fallback - you can hardcode it here for simplicity
    # Replace this with your actual folder ID
    folder_id = None  # TODO: Add your folder ID here
    
    if not folder_id:
        raise ValueError(
            "Google Drive folder ID not found!\n"
            "Please set GDRIVE_VECTORSTORE_ID in:\n"
            "- Streamlit secrets (for deployment)\n"
            "- Environment variable (for local testing)\n"
            "- Or hardcode it in gdrive_loader.py"
        )
    
    return folder_id