import streamlit as st
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except:
    PDF2IMAGE_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except:
    PYMUPDF_AVAILABLE = False
from streamlit_drawable_canvas import st_canvas
import numpy as np

st.set_page_config(page_title="PDF Signature", page_icon="✍️", layout="wide")

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first")
    st.stop()

st.title("✍️ PDF Signature Tool")
st.markdown("Upload a PDF, add your signature, position it precisely, and download the signed version!")

# Initialize session state for this page
if 'signature_x' not in st.session_state:
    st.session_state.signature_x = 400
if 'signature_y' not in st.session_state:
    st.session_state.signature_y = 100
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = 1
if 'add_date' not in st.session_state:
    st.session_state.add_date = True

def create_signature_overlay(signature_image, date_text, position, page_size, add_date=True, sig_width=150, sig_height=50):
    """Create a PDF overlay with signature and optionally date"""
    packet = io.BytesIO()
    
    # Create a new PDF with ReportLab
    c = canvas.Canvas(packet, pagesize=page_size)
    
    # Save signature image to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        signature_image.save(tmp_file.name, 'PNG')
        tmp_file_path = tmp_file.name
    
    try:
        sig_x, sig_y = position
        c.drawImage(tmp_file_path, sig_x, sig_y, width=sig_width, height=sig_height, preserveAspectRatio=True)
        
        # Add date below signature if requested
        if add_date:
            c.setFont("Helvetica", 10)
            c.drawString(sig_x + sig_width * 0.3, sig_y - 10, date_text)
    finally:
        # Clean up temp file
        os.unlink(tmp_file_path)
    
    c.save()
    
    # Move to the beginning of the BytesIO buffer
    packet.seek(0)
    return PdfReader(packet)

def add_signature_to_pdf(pdf_file, signature_image, position, selected_page=1, add_date=True, sig_dimensions=(150, 50), password=None):
    """Add signature and optionally date to specified page of PDF"""
    # Read the existing PDF
    reader = PdfReader(pdf_file)
    
    # Handle encrypted PDFs
    if reader.is_encrypted and password:
        if not reader.decrypt(password):
            raise Exception("Failed to decrypt PDF with provided password")
    
    writer = PdfWriter()
    
    # Get current date in dd mm yyyy format
    date_text = datetime.now().strftime("%d %m %Y")
    
    # Process each page
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        
        # Add signature to the selected page (convert from 1-based to 0-based indexing)
        if page_num == selected_page - 1:
            # Get page dimensions
            page_box = page.mediabox
            page_width = float(page_box.width)
            page_height = float(page_box.height)
            
            # Create overlay with signature and optionally date
            overlay = create_signature_overlay(
                signature_image, 
                date_text, 
                position,
                (page_width, page_height),
                add_date,
                sig_dimensions[0],
                sig_dimensions[1]
            )
            
            # Merge the overlay with the page
            overlay_page = overlay.pages[0]
            page.merge_page(overlay_page)
        
        # Add the page to writer (signed or unsigned)
        writer.add_page(page)
    
    # Write to bytes
    output_bytes = io.BytesIO()
    writer.write(output_bytes)
    output_bytes.seek(0)
    
    return output_bytes

def pdf_to_image(pdf_file, page_num=1, password=None):
    """Convert specified page of PDF to image for preview"""
    # Read the PDF bytes
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)  # Reset file pointer
    
    # Try PyMuPDF first (doesn't require poppler)
    if PYMUPDF_AVAILABLE:
        try:
            # Open PDF with PyMuPDF
            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Handle password if needed
            if pdf_doc.is_encrypted:
                if password:
                    if not pdf_doc.authenticate(password):
                        st.error("🔒 Incorrect password for PDF")
                        return None
                else:
                    st.error("🔒 PDF is encrypted. Please provide password above.")
                    return None
            
            # Get the specified page (0-indexed in PyMuPDF)
            page = pdf_doc[page_num - 1]
            
            # Render page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.pil_tobytes(format="PNG")
            img = Image.open(io.BytesIO(img_data))
            
            pdf_doc.close()
            return img
            
        except Exception as e:
            st.error(f"Error with PyMuPDF: {str(e)}")
            # Fall through to try pdf2image
    
    # Try pdf2image as fallback (requires poppler)
    if PDF2IMAGE_AVAILABLE:
        try:
            if password:
                images = pdf2image.convert_from_bytes(
                    pdf_bytes, 
                    first_page=page_num, 
                    last_page=page_num, 
                    dpi=150,
                    userpw=password
                )
            else:
                images = pdf2image.convert_from_bytes(
                    pdf_bytes, 
                    first_page=page_num, 
                    last_page=page_num, 
                    dpi=150
                )
            
            return images[0] if images else None
            
        except Exception as e:
            error_msg = str(e)
            if "poppler" in error_msg.lower():
                st.warning("⚠️ Poppler not installed, but PyMuPDF should work")
            else:
                st.error(f"Error with pdf2image: {error_msg}")
    
    # If neither method works
    st.warning("⚠️ PDF preview is not available")
    st.info("💡 You can still sign the PDF using manual positioning below")
    return None

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Upload PDF")
    uploaded_pdf = st.file_uploader("Choose a PDF file to sign", type="pdf", key="pdf_upload")
    
    # Page selection for multi-page PDFs
    if uploaded_pdf:
        try:
            reader = PdfReader(uploaded_pdf)
            
            # Check if PDF is encrypted
            if reader.is_encrypted:
                st.error("🔒 This PDF is encrypted/password-protected.")
                password = st.text_input("Enter PDF password to unlock:", type="password", key="pdf_password")
                if password:
                    try:
                        if reader.decrypt(password):
                            st.success("✅ PDF unlocked successfully!")
                            num_pages = len(reader.pages)
                        else:
                            st.error("❌ Incorrect password")
                            num_pages = 1
                    except Exception as e:
                        st.error(f"❌ Error decrypting PDF: {str(e)}")
                        num_pages = 1
                else:
                    st.info("Please enter the password to continue")
                    num_pages = 1
            else:
                num_pages = len(reader.pages)
            
            uploaded_pdf.seek(0)  # Reset file pointer
        except Exception as e:
            st.error(f"❌ Error reading PDF: {str(e)}")
            num_pages = 1
            uploaded_pdf.seek(0)
        
        if num_pages > 1:
            st.subheader("📑 Page Selection")
            st.session_state.selected_page = st.selectbox(
                "Select page to sign:",
                options=list(range(1, num_pages + 1)),
                index=st.session_state.selected_page - 1 if st.session_state.selected_page <= num_pages else 0,
                format_func=lambda x: f"Page {x} of {num_pages}"
            )
        else:
            st.session_state.selected_page = 1
    
    st.header("✍️ Signature")
    signature_method = st.radio("Choose signature method:", ["Upload Image", "Draw Signature"])
    
    uploaded_signature = None
    drawn_signature = None
    
    if signature_method == "Upload Image":
        uploaded_signature = st.file_uploader(
            "Choose your signature image", 
            type=["png", "jpg", "jpeg"],
            help="Upload a clear image of your signature on a white background"
        )
        
        if uploaded_signature:
            sig_image = Image.open(uploaded_signature)
            st.image(sig_image, caption="Your Signature", width=200)
    
    else:  # Draw Signature
        st.write("Draw your signature below:")
        # Create a canvas component
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=400,
            drawing_mode="freedraw",
            key="canvas",
        )
        
        # Convert canvas to image if there's drawing
        if canvas_result.image_data is not None:
            # Check if there's actual drawing (not just blank canvas)
            if np.any(canvas_result.image_data[:, :, 3] > 0):
                # Convert to PIL Image
                drawn_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                drawn_signature = drawn_image
                st.image(drawn_image, caption="Your Drawn Signature", width=200)
        
        if st.button("🔄 Clear Signature"):
            st.rerun()
    
    # Add date toggle
    st.header("⚙️ Options")
    st.session_state.add_date = st.checkbox(
        "Add date below signature", 
        value=st.session_state.add_date,
        help="Automatically add today's date below your signature"
    )

with col2:
    # Check if we have a signature (either uploaded or drawn)
    has_signature = uploaded_signature is not None or drawn_signature is not None
    
    if uploaded_pdf and has_signature:
        st.header("📍 Position Your Signature")
        
        # Get password if PDF is encrypted
        pdf_password = None
        if 'pdf_password' in st.session_state:
            pdf_password = st.session_state.get('pdf_password')
        
        # Convert selected page of PDF to image for preview
        pdf_image = pdf_to_image(uploaded_pdf, st.session_state.selected_page, pdf_password)
        
        if pdf_image:
            # Get image dimensions
            img_width, img_height = pdf_image.size
            
            # Position controls
            st.subheader("📍 Adjust Signature Position")
            st.info("💡 Use the sliders to position your signature on the document")
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                max_x = max(0, img_width - 150)
                st.session_state.signature_x = st.slider(
                    "↔️ Horizontal Position", 
                    0, 
                    max_x, 
                    value=min(st.session_state.signature_x, max_x), 
                    key="x_slider_main",
                    help="Move signature left or right"
                )
            
            with col_y:
                max_y = max(0, img_height - 50)
                st.session_state.signature_y = st.slider(
                    "↕️ Vertical Position", 
                    0, 
                    max_y, 
                    value=min(st.session_state.signature_y, max_y), 
                    key="y_slider_main",
                    help="Move signature up or down"
                )
            
            # Quick position presets
            st.subheader("⚡ Quick Position Presets")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("↙️ Bottom Left", use_container_width=True):
                    st.session_state.signature_x = 50
                    st.session_state.signature_y = img_height - 100
                    st.rerun()
            
            with col2:
                if st.button("⬇️ Bottom Center", use_container_width=True):
                    st.session_state.signature_x = (img_width - 150) // 2
                    st.session_state.signature_y = img_height - 100
                    st.rerun()
            
            with col3:
                if st.button("↘️ Bottom Right", use_container_width=True):
                    st.session_state.signature_x = img_width - 200
                    st.session_state.signature_y = img_height - 100
                    st.rerun()
            
            # Show preview with signature
            st.subheader("👁️ Preview with Signature")
            
            # Create a copy of the PDF image
            preview_img = pdf_image.copy()
            
            # Prepare signature for overlay
            if uploaded_signature:
                sig_img = Image.open(uploaded_signature)
            else:
                sig_img = drawn_signature
            sig_img = sig_img.resize((150, 50), Image.Resampling.LANCZOS)
            
            # Paste signature on preview
            preview_x = st.session_state.signature_x
            preview_y = st.session_state.signature_y
            
            if sig_img.mode == 'RGBA':
                preview_img.paste(sig_img, (preview_x, preview_y), sig_img)
            else:
                preview_img.paste(sig_img, (preview_x, preview_y))
            
            # Add date text to preview if enabled
            if st.session_state.add_date:
                draw = ImageDraw.Draw(preview_img)
                date_text = datetime.now().strftime("%d %m %Y")
                # Try to use a basic font, fallback to default if not available
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                except:
                    font = ImageFont.load_default()
                draw.text((preview_x + 65, preview_y + 52), date_text, fill='black', font=font)
            
            # Add position indicator rectangle
            draw = ImageDraw.Draw(preview_img)
            draw.rectangle(
                [preview_x, preview_y, preview_x + 150, preview_y + 50],
                outline='red',
                width=2
            )
            
            # Show preview
            page_label = f"Page {st.session_state.selected_page}" if num_pages > 1 else "Preview"
            st.image(preview_img, caption=f"{page_label} with Signature", use_container_width=True)
            
            # Process button
            if st.button("🎯 Sign PDF", type="primary", use_container_width=True):
                with st.spinner("Processing your signature..."):
                    # Get PDF page dimensions for the selected page
                    reader = PdfReader(uploaded_pdf)
                    page = reader.pages[st.session_state.selected_page - 1]
                    page_box = page.mediabox
                    pdf_width = float(page_box.width)
                    pdf_height = float(page_box.height)
                    
                    # Scale coordinates from image to PDF
                    scale_x = pdf_width / img_width
                    scale_y = pdf_height / img_height
                    
                    # Signature dimensions
                    preview_sig_width = 150
                    preview_sig_height = 50
                    pdf_sig_width = preview_sig_width * scale_x
                    pdf_sig_height = preview_sig_height * scale_y
                    
                    # Convert coordinates - PDF Y axis is bottom-up, image Y axis is top-down
                    pdf_x = st.session_state.signature_x * scale_x
                    pdf_y = pdf_height - (st.session_state.signature_y * scale_y) - pdf_sig_height
                    
                    # Process the PDF
                    uploaded_pdf.seek(0)  # Reset file pointer
                    if uploaded_signature:
                        sig_image = Image.open(uploaded_signature)
                    else:
                        sig_image = drawn_signature
                    
                    signed_pdf = add_signature_to_pdf(
                        uploaded_pdf,
                        sig_image,
                        (pdf_x, pdf_y),
                        st.session_state.selected_page,
                        st.session_state.add_date,
                        (pdf_sig_width, pdf_sig_height),
                        pdf_password
                    )
                    
                    # Offer download
                    st.success("✅ PDF signed successfully!")
                    
                    # Get original filename
                    original_name = uploaded_pdf.name
                    signed_name = original_name.replace('.pdf', '_signed.pdf')
                    
                    st.download_button(
                        label="📥 Download Signed PDF",
                        data=signed_pdf.getvalue(),
                        file_name=signed_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
        else:
            # Fallback if PDF preview fails
            st.info("📍 Manual Signature Positioning")
            st.markdown("""
            Since PDF preview is not available, you can manually set the signature position.
            Common positions:
            - **Bottom Right**: X=400, Y=50
            - **Bottom Left**: X=50, Y=50
            - **Bottom Center**: X=250, Y=50
            """)
            
            # Simple positioning without preview
            st.subheader("Set Signature Position")
            col_x, col_y = st.columns(2)
            
            with col_x:
                st.session_state.signature_x = st.number_input(
                    "X Position (from left)", 
                    min_value=0, 
                    max_value=500, 
                    value=400,
                    step=10,
                    help="Distance from left edge of the page in points"
                )
            
            with col_y:
                st.session_state.signature_y = st.number_input(
                    "Y Position (from bottom)", 
                    min_value=0, 
                    max_value=700, 
                    value=50,
                    step=10,
                    help="Distance from bottom edge of the page in points"
                )
            
            # Quick position buttons
            st.subheader("Quick Position Presets")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("↙️ Bottom Left", use_container_width=True):
                    st.session_state.signature_x = 50
                    st.session_state.signature_y = 50
                    st.rerun()
            
            with col2:
                if st.button("⬇️ Bottom Center", use_container_width=True):
                    st.session_state.signature_x = 250
                    st.session_state.signature_y = 50
                    st.rerun()
            
            with col3:
                if st.button("↘️ Bottom Right", use_container_width=True):
                    st.session_state.signature_x = 400
                    st.session_state.signature_y = 50
                    st.rerun()
            
            if st.button("🎯 Sign PDF", type="primary", use_container_width=True):
                with st.spinner("Processing your signature..."):
                    uploaded_pdf.seek(0)
                    if uploaded_signature:
                        sig_image = Image.open(uploaded_signature)
                    else:
                        sig_image = drawn_signature
                    
                    # Get password if available
                    pdf_password = st.session_state.get('pdf_password', None)
                    
                    signed_pdf = add_signature_to_pdf(
                        uploaded_pdf,
                        sig_image,
                        (st.session_state.signature_x, st.session_state.signature_y),
                        st.session_state.selected_page,
                        st.session_state.add_date,
                        (150, 50),
                        pdf_password
                    )
                    
                    st.success("✅ PDF signed successfully!")
                    
                    original_name = uploaded_pdf.name
                    signed_name = original_name.replace('.pdf', '_signed.pdf')
                    
                    st.download_button(
                        label="📥 Download Signed PDF",
                        data=signed_pdf.getvalue(),
                        file_name=signed_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
    else:
        st.info("👈 Please upload a PDF file and provide a signature (upload or draw) to begin")

# Instructions
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📝 How to Use:
    1. **Upload** your PDF document
    2. **Select** the page to sign (for multi-page PDFs)
    3. **Add** your signature (upload image or draw)
    4. **Position** your signature using the sliders
    5. **Download** your signed PDF
    """)

with col2:
    st.markdown("""
    ### ✨ Features:
    - 📸 Upload signature image or draw digitally
    - 🎚️ Precise positioning with sliders
    - ⚡ Quick position presets
    - 📅 Optional date stamp
    - 📑 Multi-page PDF support
    - 👁️ Live preview (when available)
    """)