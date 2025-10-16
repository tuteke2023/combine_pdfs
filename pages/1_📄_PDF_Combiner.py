import streamlit as st
import PyPDF2
import tempfile
import os
from io import BytesIO

st.set_page_config(page_title="PDF Combiner", page_icon="📄", layout="wide")

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first")
    if st.button("🏠 Go to Home Page", type="primary"):
        st.switch_page("app.py")
    st.stop()

def get_pdf_info(pdf_file):
    """Extract information from PDF file"""
    pdf_file.seek(0)
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        # Try to extract text from first page for preview
        first_page_text = ""
        if num_pages > 0:
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            # Get first 200 characters for preview
            first_page_text = text[:200] + "..." if len(text) > 200 else text
            first_page_text = first_page_text.replace('\n', ' ').strip()
        
        pdf_file.seek(0)
        return {
            "pages": num_pages,
            "preview_text": first_page_text if first_page_text else "No text content available"
        }
    except Exception as e:
        return {
            "pages": "Unknown",
            "preview_text": f"Error reading PDF: {str(e)}"
        }

def create_pdf_card(file, index, position):
    """Create a card display for a PDF file"""
    info = get_pdf_info(file)
    
    with st.container():
        card = st.container()
        with card:
            st.markdown(
                f"""
                <div style="
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    background-color: #f9f9f9;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h4 style="margin: 0 0 10px 0; color: #333;">
                        📄 Position #{position + 1}
                    </h4>
                    <p style="margin: 5px 0; font-weight: bold; color: #555;">
                        {file.name}
                    </p>
                    <p style="margin: 5px 0; color: #666; font-size: 0.9em;">
                        📑 Pages: {info['pages']}
                    </p>
                    <p style="margin: 5px 0; color: #666; font-size: 0.85em;">
                        Size: {file.size / 1024:.1f} KB
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.expander("📖 Preview first page text"):
                st.text(info['preview_text'])
            
            return info

# Main app header
st.title("📄 PDF Combiner")
st.markdown("Upload PDFs via drag & drop or browse. Preview and reorder files before combining.")

# File uploader with drag and drop
uploaded_files = st.file_uploader(
    "📥 Drag and drop PDF files here or click to browse", 
    type="pdf", 
    accept_multiple_files=True,
    help="You can drag multiple PDF files directly onto this area"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
    
    if len(uploaded_files) > 1:
        st.markdown("---")
        st.subheader("📋 Arrange Your PDFs")
        st.info("💡 Use the select boxes below each file to change their order in the final combined PDF")
        
        # Initialize file order in session state
        if 'file_order' not in st.session_state or len(st.session_state.file_order) != len(uploaded_files):
            st.session_state.file_order = list(range(len(uploaded_files)))
        
        # Create columns for file cards
        num_cols = min(3, len(uploaded_files))  # Max 3 columns
        cols = st.columns(num_cols)
        
        # Track the new order
        new_order = []
        
        # Display files in grid layout
        for i, file_idx in enumerate(st.session_state.file_order):
            col_idx = i % num_cols
            with cols[col_idx]:
                # Display file card
                file = uploaded_files[file_idx]
                create_pdf_card(file, file_idx, i)
                
                # Order selector
                new_position = st.selectbox(
                    "Move to position:",
                    options=list(range(len(uploaded_files))),
                    index=i,
                    format_func=lambda x: f"Position {x + 1}",
                    key=f"pos_{file_idx}_{i}"
                )
                new_order.append((file_idx, new_position))
        
        # Update order based on selections
        sorted_order = sorted(new_order, key=lambda x: x[1])
        st.session_state.file_order = [item[0] for item in sorted_order]
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Reset Order", type="secondary", use_container_width=True):
                st.session_state.file_order = list(range(len(uploaded_files)))
                st.rerun()
        
        with col2:
            # Display current order summary
            with st.popover("📊 Current Order"):
                st.markdown("**Files will be combined in this order:**")
                for i, idx in enumerate(st.session_state.file_order):
                    st.write(f"{i+1}. {uploaded_files[idx].name}")
        
        with col3:
            if st.button("🔀 Combine PDFs", type="primary", use_container_width=True):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    with st.spinner("Combining PDFs..."):
                        pdf_writer = PyPDF2.PdfWriter()
                        total_files = len(st.session_state.file_order)
                        
                        for i, idx in enumerate(st.session_state.file_order):
                            status_text.text(f"Processing {uploaded_files[idx].name}...")
                            progress_bar.progress((i + 1) / total_files)
                            
                            pdf_reader = PyPDF2.PdfReader(uploaded_files[idx])
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                pdf_writer.add_page(page)
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            pdf_writer.write(tmp_file)
                            tmp_file_path = tmp_file.name
                        
                        # Read the combined PDF
                        with open(tmp_file_path, "rb") as file:
                            pdf_data = file.read()
                        
                        # Clean up
                        os.unlink(tmp_file_path)
                        
                        progress_bar.progress(1.0)
                        status_text.text("✅ PDFs combined successfully!")
                        
                        # Count total pages in combined PDF
                        combined_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
                        total_pages = len(combined_reader.pages)
                        
                        st.success(f"✅ Successfully combined {total_files} PDFs into 1 file with {total_pages} total pages!")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Combined PDF",
                            data=pdf_data,
                            file_name="combined.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.info("Please check that all uploaded files are valid PDFs and try again.")
    
    elif len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 PDF files to combine.")
        # Still show preview for single file
        st.markdown("---")
        st.subheader("📄 File Preview")
        create_pdf_card(uploaded_files[0], 0, 0)
else:
    # Instructions when no files are uploaded
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            ### 📝 How to Use:
            1. **Drag & Drop** or **Browse** to upload PDF files
            2. **Preview** each PDF's information
            3. **Reorder** files using the position selectors
            4. **Combine** all PDFs into one
            5. **Download** your combined PDF
            """
        )
    
    with col2:
        st.markdown(
            """
            ### ✨ Features:
            - 📥 Drag & drop file upload
            - 👁️ Preview PDF information
            - 🔄 Easy file reordering
            - 📊 Page count display
            - 📈 Progress tracking
            """
        )
    
    st.info("💡 Tip: You can select and drag multiple PDF files at once directly onto the upload area above!")