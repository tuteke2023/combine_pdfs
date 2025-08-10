import streamlit as st
import PyPDF2
import tempfile
import os
from pathlib import Path
import hashlib
import hmac

st.set_page_config(page_title="PDF Combiner", page_icon="📄")

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔐 PDF Combiner - Login")
    st.text_input(
        "Password", 
        type="password", 
        on_change=password_entered, 
        key="password",
        help="Enter the password to access the PDF Combiner"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
    
    st.info("💡 Contact the administrator if you don't have the password.")
    return False

if not check_password():
    st.stop()

st.title("📄 PDF Combiner")
st.markdown("Upload multiple PDF files and combine them into a single PDF. You can reorder the files before combining.")

col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🚪 Logout", type="secondary"):
        st.session_state["password_correct"] = False
        st.rerun()

uploaded_files = st.file_uploader(
    "Choose PDF files", 
    type="pdf", 
    accept_multiple_files=True,
    help="Select one or more PDF files to combine"
)

if uploaded_files:
    st.subheader("📁 Uploaded Files")
    st.info(f"You have uploaded {len(uploaded_files)} file(s)")
    
    if len(uploaded_files) > 1:
        st.subheader("📋 File Order")
        st.markdown("Drag to reorder the files:")
        
        if 'file_order' not in st.session_state:
            st.session_state.file_order = list(range(len(uploaded_files)))
        
        if len(st.session_state.file_order) != len(uploaded_files):
            st.session_state.file_order = list(range(len(uploaded_files)))
        
        ordered_files = []
        for i in range(len(uploaded_files)):
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.write(f"#{i+1}")
            
            with col2:
                file_index = st.selectbox(
                    f"Position {i+1}",
                    options=range(len(uploaded_files)),
                    format_func=lambda x: uploaded_files[x].name,
                    key=f"select_{i}",
                    label_visibility="collapsed"
                )
                ordered_files.append(file_index)
            
            with col3:
                st.write(f"📄")
        
        st.session_state.file_order = ordered_files
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Order", type="secondary", use_container_width=True):
                st.session_state.file_order = list(range(len(uploaded_files)))
                st.rerun()
        
        with col2:
            if st.button("🔀 Combine PDFs", type="primary", use_container_width=True):
                try:
                    with st.spinner("Combining PDFs..."):
                        pdf_writer = PyPDF2.PdfWriter()
                        
                        for idx in st.session_state.file_order:
                            pdf_reader = PyPDF2.PdfReader(uploaded_files[idx])
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                pdf_writer.add_page(page)
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            pdf_writer.write(tmp_file)
                            tmp_file_path = tmp_file.name
                        
                        with open(tmp_file_path, "rb") as file:
                            pdf_data = file.read()
                        
                        os.unlink(tmp_file_path)
                        
                        st.success("✅ PDFs combined successfully!")
                        
                        st.download_button(
                            label="📥 Download Combined PDF",
                            data=pdf_data,
                            file_name="combined.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
    elif len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 PDF files to combine.")
    
else:
    st.info("👆 Please upload PDF files to get started.")

st.divider()
st.markdown(
    """
    ### 📝 Instructions:
    1. Click on **Browse files** to upload multiple PDF files
    2. Use the dropdown menus to reorder the files if needed
    3. Click **Combine PDFs** to merge them
    4. Download your combined PDF file
    """
)