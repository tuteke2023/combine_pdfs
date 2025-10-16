import streamlit as st
import io
from pypdf import PdfReader, PdfWriter
try:
    import fitz  # PyMuPDF for page preview
    PYMUPDF_AVAILABLE = True
except:
    PYMUPDF_AVAILABLE = False
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="PDF Page Manager", page_icon="📑", layout="wide")

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first")
    if st.button("🏠 Go to Home Page", type="primary"):
        st.switch_page("app.py")
    st.stop()

st.title("📑 PDF Page Manager")
st.markdown("Reorder, delete, or extract pages from your PDF with visual preview")

# Initialize session state
if 'page_order' not in st.session_state:
    st.session_state.page_order = []
if 'deleted_pages' not in st.session_state:
    st.session_state.deleted_pages = set()
if 'pdf_pages' not in st.session_state:
    st.session_state.pdf_pages = []
if 'current_file_name' not in st.session_state:
    st.session_state.current_file_name = None

def pdf_page_to_image(pdf_file, page_num, password=None):
    """Convert a specific PDF page to image for preview"""
    if not PYMUPDF_AVAILABLE:
        return None
    
    try:
        # Read the PDF bytes fresh each time
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        # Open with PyMuPDF
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Handle password if needed
        if pdf_doc.is_encrypted:
            if password:
                if not pdf_doc.authenticate(password):
                    return None
            else:
                return None
        
        # Check page number is valid
        if page_num >= len(pdf_doc):
            pdf_doc.close()
            return None
        
        # Get the page (0-indexed)
        page = pdf_doc[page_num]
        
        # Render page to image with reasonable resolution
        mat = fitz.Matrix(1.5, 1.5)  # 1.5x zoom for better quality but not too large
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.pil_tobytes(format="PNG")
        img = Image.open(io.BytesIO(img_data))
        
        pdf_doc.close()
        return img
        
    except Exception as e:
        # Don't show error for each page, just return None
        print(f"Could not convert page {page_num + 1}: {str(e)}")
        return None

def extract_pages_info(pdf_file, password=None):
    """Extract information about each page"""
    pdf_file.seek(0)
    reader = PdfReader(pdf_file)
    
    # Handle encrypted PDFs
    if reader.is_encrypted and password:
        if not reader.decrypt(password):
            st.error("Failed to decrypt PDF with provided password")
            return []
    
    pages_info = []
    
    for i in range(len(reader.pages)):
        page_info = {
            'page_num': i + 1,  # 1-indexed for display
            'original_index': i,  # 0-indexed for processing
            'preview': pdf_page_to_image(pdf_file, i, password)  # Pass file object directly
        }
        pages_info.append(page_info)
    
    return pages_info

def create_modified_pdf(pdf_file, page_order, deleted_pages, password=None):
    """Create a new PDF with reordered pages and deleted pages removed"""
    pdf_file.seek(0)
    reader = PdfReader(pdf_file)
    
    # Handle encrypted PDFs
    if reader.is_encrypted and password:
        if not reader.decrypt(password):
            raise Exception("Failed to decrypt PDF with provided password")
    
    writer = PdfWriter()
    
    # Add pages in the new order, skipping deleted ones
    for page_idx in page_order:
        if page_idx not in deleted_pages:
            writer.add_page(reader.pages[page_idx])
    
    # Write to bytes
    output_bytes = io.BytesIO()
    writer.write(output_bytes)
    output_bytes.seek(0)
    
    return output_bytes

# Main UI
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📤 Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file to manage",
        type="pdf",
        key="pdf_page_manager",
        help="Upload a PDF to reorder or delete pages"
    )
    
    pdf_password = None
    if uploaded_file:
        # Check if it's a new file
        if st.session_state.current_file_name != uploaded_file.name:
            st.session_state.current_file_name = uploaded_file.name
            st.session_state.page_order = []
            st.session_state.deleted_pages = set()
            st.session_state.pdf_pages = []
        
        # Check if PDF is encrypted
        try:
            reader = PdfReader(uploaded_file)
            if reader.is_encrypted:
                st.warning("🔒 This PDF is encrypted")
                pdf_password = st.text_input("Enter PDF password:", type="password", key="pdf_page_password")
                if pdf_password:
                    if reader.decrypt(pdf_password):
                        st.success("✅ PDF unlocked!")
                    else:
                        st.error("❌ Incorrect password")
                        pdf_password = None
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
    
    if uploaded_file and (not reader.is_encrypted or pdf_password):
        # Extract pages info if not already done
        if not st.session_state.pdf_pages:
            with st.spinner("Loading PDF pages..."):
                pages_info = extract_pages_info(uploaded_file, pdf_password)
                st.session_state.pdf_pages = pages_info
                st.session_state.page_order = [p['original_index'] for p in pages_info]
        
        st.success(f"✅ Loaded {len(st.session_state.pdf_pages)} pages")
        
        # Check if previews are available
        has_preview = any(p['preview'] is not None for p in st.session_state.pdf_pages)
        if not has_preview:
            st.info("ℹ️ Visual previews not available, but you can still manage pages")
        
        # Controls
        st.header("🎛️ Page Controls")
        
        # Quick actions
        st.subheader("Quick Actions")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔄 Reset Order", use_container_width=True):
                st.session_state.page_order = [p['original_index'] for p in st.session_state.pdf_pages]
                st.session_state.deleted_pages = set()
                st.rerun()
        
        with col_b:
            if st.button("🔀 Reverse Order", use_container_width=True):
                current_order = [p for p in st.session_state.page_order if p not in st.session_state.deleted_pages]
                st.session_state.page_order = list(reversed(current_order))
                st.rerun()
        
        # Page range operations
        st.subheader("Page Range Operations")
        
        # Delete range
        with st.expander("🗑️ Delete Page Range"):
            col_start, col_end = st.columns(2)
            with col_start:
                delete_start = st.number_input(
                    "From page",
                    min_value=1,
                    max_value=len(st.session_state.pdf_pages),
                    value=1
                )
            with col_end:
                delete_end = st.number_input(
                    "To page",
                    min_value=delete_start,
                    max_value=len(st.session_state.pdf_pages),
                    value=delete_start
                )
            
            if st.button("Delete Range", type="secondary"):
                for i in range(delete_start - 1, delete_end):
                    st.session_state.deleted_pages.add(st.session_state.pdf_pages[i]['original_index'])
                st.success(f"Marked pages {delete_start}-{delete_end} for deletion")
                st.rerun()
        
        # Extract range
        with st.expander("✂️ Extract Page Range"):
            col_start, col_end = st.columns(2)
            with col_start:
                extract_start = st.number_input(
                    "From page",
                    min_value=1,
                    max_value=len(st.session_state.pdf_pages),
                    value=1,
                    key="extract_start"
                )
            with col_end:
                extract_end = st.number_input(
                    "To page",
                    min_value=extract_start,
                    max_value=len(st.session_state.pdf_pages),
                    value=len(st.session_state.pdf_pages),
                    key="extract_end"
                )
            
            if st.button("Extract Range Only", type="secondary"):
                # Keep only the selected range
                new_order = []
                for i in range(extract_start - 1, extract_end):
                    new_order.append(st.session_state.pdf_pages[i]['original_index'])
                st.session_state.page_order = new_order
                # Mark all others as deleted
                st.session_state.deleted_pages = set()
                for p in st.session_state.pdf_pages:
                    if p['original_index'] not in new_order:
                        st.session_state.deleted_pages.add(p['original_index'])
                st.success(f"Extracted pages {extract_start}-{extract_end}")
                st.rerun()
        
        # Statistics
        st.subheader("📊 Statistics")
        active_pages = len([p for p in st.session_state.page_order if p not in st.session_state.deleted_pages])
        st.info(f"Active pages: {active_pages} / {len(st.session_state.pdf_pages)}")
        if st.session_state.deleted_pages:
            st.warning(f"Pages marked for deletion: {len(st.session_state.deleted_pages)}")
        
        # Process button
        st.header("💾 Save Changes")
        if active_pages > 0:
            if st.button("🎯 Create Modified PDF", type="primary", use_container_width=True):
                with st.spinner("Creating modified PDF..."):
                    try:
                        uploaded_file.seek(0)
                        modified_pdf = create_modified_pdf(
                            uploaded_file,
                            st.session_state.page_order,
                            st.session_state.deleted_pages,
                            pdf_password
                        )
                        
                        # Generate filename
                        original_name = uploaded_file.name
                        modified_name = original_name.replace('.pdf', '_modified.pdf')
                        
                        st.success("✅ PDF modified successfully!")
                        st.download_button(
                            label="📥 Download Modified PDF",
                            data=modified_pdf.getvalue(),
                            file_name=modified_name,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error creating modified PDF: {str(e)}")
        else:
            st.warning("No pages to save (all pages deleted)")

with col2:
    if uploaded_file and st.session_state.pdf_pages:
        st.header("📄 Page Preview & Management")
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["Grid View", "List View"])
        
        with tab1:
            # Grid view with previews
            st.markdown("**Drag pages to reorder, click to delete/restore**")
            
            # Display pages in a grid
            cols_per_row = 3
            active_pages = [p for p in st.session_state.page_order if p not in st.session_state.deleted_pages]
            
            for row_start in range(0, len(st.session_state.page_order), cols_per_row):
                cols = st.columns(cols_per_row)
                for col_idx, col in enumerate(cols):
                    page_idx = row_start + col_idx
                    if page_idx < len(st.session_state.page_order):
                        original_idx = st.session_state.page_order[page_idx]
                        page_info = next(p for p in st.session_state.pdf_pages if p['original_index'] == original_idx)
                        
                        with col:
                            # Check if page is deleted
                            is_deleted = original_idx in st.session_state.deleted_pages
                            
                            # Container for each page
                            if is_deleted:
                                st.markdown(f"~~Page {page_info['page_num']}~~ **DELETED**")
                            else:
                                st.markdown(f"**Page {page_info['page_num']}**")
                            
                            # Show preview if available
                            if page_info['preview'] and not is_deleted:
                                st.image(page_info['preview'], use_container_width=True)
                            elif is_deleted:
                                st.info("🗑️ Marked for deletion")
                            else:
                                # Show page info even without preview
                                st.info(f"📄 Page {page_info['page_num']}\n(Preview not available)")
                            
                            # Control buttons
                            col_up, col_down, col_del = st.columns(3)
                            
                            with col_up:
                                if page_idx > 0 and not is_deleted:
                                    if st.button("⬆️", key=f"up_{original_idx}", use_container_width=True):
                                        # Swap with previous
                                        st.session_state.page_order[page_idx], st.session_state.page_order[page_idx-1] = \
                                            st.session_state.page_order[page_idx-1], st.session_state.page_order[page_idx]
                                        st.rerun()
                            
                            with col_down:
                                if page_idx < len(st.session_state.page_order) - 1 and not is_deleted:
                                    if st.button("⬇️", key=f"down_{original_idx}", use_container_width=True):
                                        # Swap with next
                                        st.session_state.page_order[page_idx], st.session_state.page_order[page_idx+1] = \
                                            st.session_state.page_order[page_idx+1], st.session_state.page_order[page_idx]
                                        st.rerun()
                            
                            with col_del:
                                if is_deleted:
                                    if st.button("♻️", key=f"restore_{original_idx}", use_container_width=True):
                                        st.session_state.deleted_pages.remove(original_idx)
                                        st.rerun()
                                else:
                                    if st.button("🗑️", key=f"del_{original_idx}", use_container_width=True):
                                        st.session_state.deleted_pages.add(original_idx)
                                        st.rerun()
        
        with tab2:
            # List view for precise ordering
            st.markdown("**Reorder pages using the number inputs**")
            
            # Create a list of pages with order inputs
            new_order = {}
            for i, original_idx in enumerate(st.session_state.page_order):
                page_info = next(p for p in st.session_state.pdf_pages if p['original_index'] == original_idx)
                is_deleted = original_idx in st.session_state.deleted_pages
                
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                
                with col1:
                    if not is_deleted:
                        new_pos = st.number_input(
                            "Position",
                            min_value=1,
                            max_value=len(st.session_state.page_order),
                            value=i + 1,
                            key=f"pos_{original_idx}"
                        )
                        new_order[original_idx] = new_pos - 1
                    else:
                        st.write("--")
                
                with col2:
                    if is_deleted:
                        st.write(f"~~Page {page_info['page_num']}~~")
                    else:
                        st.write(f"Page {page_info['page_num']}")
                
                with col3:
                    if is_deleted:
                        st.write("🗑️ Marked for deletion")
                    else:
                        st.write("✅ Active")
                
                with col4:
                    if is_deleted:
                        if st.button("Restore", key=f"restore_list_{original_idx}"):
                            st.session_state.deleted_pages.remove(original_idx)
                            st.rerun()
                    else:
                        if st.button("Delete", key=f"del_list_{original_idx}"):
                            st.session_state.deleted_pages.add(original_idx)
                            st.rerun()
            
            # Apply new order button
            if st.button("Apply New Order", type="secondary"):
                # Sort pages by their new positions
                sorted_pages = sorted(new_order.items(), key=lambda x: x[1])
                st.session_state.page_order = [page_idx for page_idx, _ in sorted_pages]
                # Add deleted pages at the end (they won't be included in output anyway)
                for p in st.session_state.deleted_pages:
                    if p not in st.session_state.page_order:
                        st.session_state.page_order.append(p)
                st.success("✅ New order applied!")
                st.rerun()
    
    elif uploaded_file:
        st.info("🔐 Please enter the password to unlock the PDF")
    else:
        st.info("👈 Please upload a PDF file to manage its pages")

# Instructions
st.markdown("---")
with st.expander("📖 How to Use", expanded=False):
    st.markdown("""
    ### 📑 PDF Page Manager Guide
    
    **Features:**
    - 📄 **Visual Preview**: See each page before making changes
    - 🔄 **Reorder Pages**: Move pages up/down or set specific positions
    - 🗑️ **Delete Pages**: Remove unwanted pages
    - ✂️ **Extract Range**: Keep only specific page ranges
    - ♻️ **Restore Pages**: Undo deletions before saving
    
    **How to Use:**
    1. **Upload** your PDF file
    2. **Preview** pages in Grid or List view
    3. **Reorder** by:
       - Using ⬆️⬇️ buttons in Grid view
       - Setting position numbers in List view
       - Using Quick Actions (Reverse Order)
    4. **Delete** pages by:
       - Clicking 🗑️ on individual pages
       - Using Delete Range for multiple pages
    5. **Extract** specific ranges with Extract Range
    6. **Save** your modified PDF
    
    **Tips:**
    - 💡 Grid View is best for visual preview
    - 💡 List View is best for precise ordering
    - 💡 Deleted pages can be restored before saving
    - 💡 Use Extract Range to quickly keep only needed pages
    
    **Common Use Cases:**
    - Remove blank pages from scanned documents
    - Extract specific sections from reports
    - Reorder pages in merged documents
    - Remove confidential pages before sharing
    """)

with st.expander("⚡ Keyboard Shortcuts", expanded=False):
    st.markdown("""
    ### Keyboard Navigation (when focused on buttons)
    
    - **Tab**: Navigate between controls
    - **Enter**: Activate focused button
    - **Space**: Alternative to activate button
    
    ### Quick Actions
    - Use number inputs in List View for fast reordering
    - Batch operations with Range tools
    """)