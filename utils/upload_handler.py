"""
Upload Handler - Clean file upload system
Handles PDFs, images with professional UI
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import shutil
from PIL import Image
import fitz  # PyMuPDF

class UploadHandler:
    def __init__(self, upload_dir="student_uploads"):
        """Initialize upload handler"""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.pdf_dir = self.upload_dir / "pdfs"
        self.image_dir = self.upload_dir / "images"
        self.pdf_dir.mkdir(exist_ok=True)
        self.image_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, uploaded_file):
        """Save uploaded file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = uploaded_file.name
        file_ext = Path(original_name).suffix.lower()
        
        safe_name = f"{timestamp}_{original_name}"
        
        if file_ext == '.pdf':
            save_path = self.pdf_dir / safe_name
            file_type = "PDF"
        elif file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            save_path = self.image_dir / safe_name
            file_type = "Image"
        else:
            return None
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        file_size = save_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        return {
            'path': str(save_path),
            'type': file_type,
            'name': original_name,
            'size_mb': f"{size_mb:.2f}",
            'timestamp': timestamp
        }
    
    def list_uploaded_files(self):
        """List all uploaded files"""
        files = []
        
        for pdf_file in self.pdf_dir.glob("*.pdf"):
            files.append({
                'name': pdf_file.name,
                'type': 'PDF',
                'path': str(pdf_file),
                'size_mb': f"{pdf_file.stat().st_size / (1024*1024):.2f}"
            })
        
        for img_file in self.image_dir.glob("*"):
            if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                files.append({
                    'name': img_file.name,
                    'type': 'Image',
                    'path': str(img_file),
                    'size_mb': f"{img_file.stat().st_size / (1024*1024):.2f}"
                })
        
        return sorted(files, key=lambda x: x['name'], reverse=True)
    
    def delete_file(self, file_path):
        """Delete an uploaded file"""
        try:
            Path(file_path).unlink()
            return True
        except Exception as e:
            return False
    
    def get_upload_stats(self):
        """Get upload statistics"""
        pdf_count = len(list(self.pdf_dir.glob("*.pdf")))
        img_count = len(list(self.image_dir.glob("*.[pj][np]g")))
        img_count += len(list(self.image_dir.glob("*.jpeg")))
        
        total_size = 0
        for file in self.pdf_dir.glob("*"):
            total_size += file.stat().st_size
        for file in self.image_dir.glob("*"):
            total_size += file.stat().st_size
        
        return {
            'pdf_count': pdf_count,
            'image_count': img_count,
            'total_size_mb': f"{total_size / (1024*1024):.2f}"
        }


def render_upload_ui():
    """Clean upload UI with + button"""
    handler = UploadHandler()
    
    # Upload button
    if st.button("➕ Upload File", use_container_width=True, type="primary"):
        st.session_state.show_upload = True
    
    # Show upload dialog
    if st.session_state.get('show_upload', False):
        with st.container():
            st.markdown("### Upload Document")
            
            uploaded_file = st.file_uploader(
                "Choose file",
                type=['pdf', 'png', 'jpg', 'jpeg'],
                help="PDF, PNG, JPG (Max 200MB)",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_upload = False
                    st.rerun()
            
            with col2:
                if uploaded_file and st.button("Upload", use_container_width=True, type="primary"):
                    result = handler.save_uploaded_file(uploaded_file)
                    if result:
                        st.success(f"✓ {result['name']} uploaded")
                        st.session_state.show_upload = False
                        st.rerun()
    
    # Show stats
    stats = handler.get_upload_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("PDFs", stats['pdf_count'])
    col2.metric("Images", stats['image_count'])
    col3.metric("Total", f"{stats['total_size_mb']}MB")
    
    # List files
    with st.expander("📁 Uploaded Files"):
        files = handler.list_uploaded_files()
        if files:
            for file in files[:10]:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(file['name'][:40])
                col2.write(file['type'])
                if col3.button("🗑️", key=f"del_{file['name']}"):
                    handler.delete_file(file['path'])
                    st.rerun()
        else:
            st.info("No files uploaded yet")