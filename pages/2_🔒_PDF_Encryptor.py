import streamlit as st
import PyPDF2
import tempfile
import os
import string
import secrets
from io import BytesIO
import zipfile

st.set_page_config(page_title="PDF Encryptor", page_icon="🔒", layout="wide")

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first")
    st.stop()

def generate_secure_password(length=16):
    """Generate a cryptographically secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Remove problematic characters for better compatibility
    alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def encrypt_pdf(pdf_file, password):
    """Encrypt a PDF file with the given password"""
    try:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_writer = PyPDF2.PdfWriter()
        
        # Copy all pages to writer
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        # Encrypt the PDF
        pdf_writer.encrypt(password, password, use_128bit=True)
        
        # Write to bytes
        output_stream = BytesIO()
        pdf_writer.write(output_stream)
        output_stream.seek(0)
        
        return output_stream.getvalue()
    except Exception as e:
        return None, str(e)

def get_pdf_info(pdf_file):
    """Extract basic information from PDF file"""
    pdf_file.seek(0)
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        pdf_file.seek(0)
        return {"pages": num_pages, "error": None}
    except Exception as e:
        return {"pages": 0, "error": str(e)}

# Main page
st.title("🔒 PDF Encryptor")
st.markdown("Protect your PDF files with strong password encryption. Each file will receive a unique, randomly generated password.")

# Password generation settings
with st.expander("⚙️ Password Settings", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        password_length = st.slider(
            "Password Length",
            min_value=8,
            max_value=32,
            value=16,
            help="Longer passwords are more secure"
        )
    with col2:
        include_symbols = st.checkbox(
            "Include symbols",
            value=True,
            help="Include special characters like !@#$%"
        )

# File uploader
uploaded_files = st.file_uploader(
    "📤 Upload PDF files to encrypt",
    type="pdf",
    accept_multiple_files=True,
    help="You can upload multiple PDF files at once"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
    
    # Display file information
    st.markdown("---")
    st.subheader("📋 Files to Encrypt")
    
    file_info = []
    for file in uploaded_files:
        info = get_pdf_info(file)
        file_info.append({
            "name": file.name,
            "size": file.size / 1024,  # Convert to KB
            "pages": info["pages"],
            "error": info["error"]
        })
    
    # Display file table
    cols = st.columns([3, 1, 1, 2])
    cols[0].markdown("**File Name**")
    cols[1].markdown("**Pages**")
    cols[2].markdown("**Size (KB)**")
    cols[3].markdown("**Status**")
    
    for info in file_info:
        cols = st.columns([3, 1, 1, 2])
        cols[0].text(info["name"])
        cols[1].text(str(info["pages"]) if not info["error"] else "❌")
        cols[2].text(f"{info['size']:.1f}")
        cols[3].text("✅ Ready" if not info["error"] else f"⚠️ {info['error'][:20]}...")
    
    st.markdown("---")
    
    # Encrypt button
    if st.button("🔐 Encrypt All PDFs", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        encrypted_files = []
        passwords = {}
        errors = []
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Encrypting {file.name}...")
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Generate unique password for this file
            if include_symbols:
                password = generate_secure_password(password_length)
            else:
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for _ in range(password_length))
            
            # Encrypt the PDF
            encrypted_data = encrypt_pdf(file, password)
            
            if encrypted_data:
                encrypted_files.append({
                    "name": file.name.replace(".pdf", "_encrypted.pdf"),
                    "data": encrypted_data,
                    "original_name": file.name
                })
                passwords[file.name] = password
            else:
                errors.append(file.name)
        
        progress_bar.progress(1.0)
        status_text.text("✅ Encryption complete!")
        
        if encrypted_files:
            st.success(f"🎉 Successfully encrypted {len(encrypted_files)} file(s)!")
            
            # Display passwords
            st.markdown("---")
            st.subheader("🔑 Generated Passwords")
            st.warning("⚠️ **IMPORTANT**: Save these passwords! You'll need them to open the encrypted PDFs.")
            st.info("💡 **Tip**: Click on any password field below and press Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C to copy.")
            
            # Create a text summary of passwords
            password_summary = "PDF ENCRYPTION PASSWORDS\n" + "="*50 + "\n\n"
            for original_name, pwd in passwords.items():
                password_summary += f"File: {original_name}\nPassword: {pwd}\n\n"
                
            # Display passwords in two formats for easy copying
            
            # Format 1: Individual password fields
            st.markdown("##### 📋 Individual Passwords (click field and Ctrl+A then Ctrl+C to copy)")
            password_container = st.container()
            with password_container:
                for idx, (original_name, pwd) in enumerate(passwords.items()):
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown(f"**{original_name}**")
                    with col2:
                        # Create a text input with the password for easy copying
                        st.text_input(
                            "Password",
                            value=pwd,
                            key=f"pwd_display_{idx}",
                            label_visibility="collapsed",
                            help="Click to select all, then Ctrl+C (or Cmd+C) to copy"
                        )
            
            # Format 2: All passwords in one text area for bulk copying
            with st.expander("📄 All Passwords (for bulk copying)"):
                all_passwords_text = ""
                for original_name, pwd in passwords.items():
                    all_passwords_text += f"{original_name}: {pwd}\n"
                
                st.text_area(
                    "All Passwords",
                    value=all_passwords_text,
                    height=min(300, len(passwords) * 30),
                    label_visibility="collapsed",
                    help="Select all text with Ctrl+A (or Cmd+A) then copy with Ctrl+C (or Cmd+C)"
                )
            
            st.markdown("---")
            
            # Download options
            st.subheader("📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download passwords as text file
                st.download_button(
                    label="📝 Download Password List",
                    data=password_summary,
                    file_name="pdf_passwords.txt",
                    mime="text/plain",
                    use_container_width=True,
                    help="Download a text file with all passwords"
                )
            
            with col2:
                # Create and download ZIP file if multiple files
                if len(encrypted_files) > 1:
                    # Create ZIP file in memory
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        # Add encrypted PDFs
                        for ef in encrypted_files:
                            zip_file.writestr(ef["name"], ef["data"])
                        # Add password file
                        zip_file.writestr("passwords.txt", password_summary)
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="📦 Download All (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="encrypted_pdfs.zip",
                        mime="application/zip",
                        use_container_width=True,
                        help="Download all encrypted PDFs and passwords in a ZIP file"
                    )
                else:
                    # Single file download
                    st.download_button(
                        label="📄 Download Encrypted PDF",
                        data=encrypted_files[0]["data"],
                        file_name=encrypted_files[0]["name"],
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            # Individual file downloads
            if len(encrypted_files) > 1:
                st.markdown("---")
                st.subheader("📄 Individual Downloads")
                
                cols_per_row = 3
                for i in range(0, len(encrypted_files), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(min(cols_per_row, len(encrypted_files) - i)):
                        with cols[j]:
                            ef = encrypted_files[i + j]
                            st.download_button(
                                label=f"📥 {ef['original_name']}",
                                data=ef["data"],
                                file_name=ef["name"],
                                mime="application/pdf",
                                key=f"dl_{i}_{j}"
                            )
        
        if errors:
            st.error(f"❌ Failed to encrypt {len(errors)} file(s): {', '.join(errors)}")

else:
    # Instructions
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 How It Works:
        1. **Upload** one or more PDF files
        2. **Configure** password settings (optional)
        3. **Click Encrypt** to secure your PDFs
        4. **Save** the generated passwords
        5. **Download** your encrypted PDFs
        """)
        
    with col2:
        st.markdown("""
        ### 🛡️ Security Features:
        - 🎲 Cryptographically secure random passwords
        - 🔐 128-bit AES encryption
        - 🔑 Unique password for each file
        - 📋 Password list download
        - 📦 Bulk download as ZIP
        """)
    
    st.info("""
    💡 **Tips:**
    - Each PDF receives a unique password for maximum security
    - Passwords are randomly generated using cryptographically secure methods
    - Save the password file immediately - passwords cannot be recovered if lost!
    - Encrypted PDFs require the password to open in any PDF reader
    """)