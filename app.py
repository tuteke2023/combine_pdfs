import streamlit as st
import hmac

st.set_page_config(
    page_title="TTA PDF Tool Suite", 
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    st.title("🔐 TTA PDF Tool Suite - Login")
    st.text_input(
        "Password", 
        type="password", 
        on_change=password_entered, 
        key="password",
        help="Enter the password to access the PDF Tools"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
    
    st.info("💡 Contact the administrator if you don't have the password.")
    return False

if not check_password():
    st.stop()

# Main page content
st.title("📄 TTA PDF Tool Suite")
st.markdown("Welcome to the TTA PDF Tool Suite! Choose a tool from the sidebar to get started.")

col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🚪 Logout", type="secondary"):
        st.session_state["password_correct"] = False
        st.rerun()

st.markdown("---")

# Display available tools
st.subheader("🛠️ Available Tools")

# First row of tools
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🔀 PDF Combiner
    Combine multiple PDF files into a single document:
    - Drag & drop upload
    - Preview and reorder
    - Download combined PDF
    
    **→ '1_📄_PDF_Combiner'**
    """)

with col2:
    st.markdown("""
    ### 🔒 PDF Encryptor
    Protect PDFs with passwords:
    - Bulk encryption
    - Secure passwords
    - ZIP download
    
    **→ '2_🔒_PDF_Encryptor'**
    """)

with col3:
    st.markdown("""
    ### ✍️ PDF Signature
    Add signatures to PDFs:
    - Draw or upload signature
    - Interactive positioning
    - Date stamp option
    
    **→ '3_✍️_PDF_Signature'**
    """)

# Second row for new tool
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    ### ⬛ PDF Redaction
    Remove sensitive information:
    - Auto-detect TFN/ABN
    - Pattern matching
    - Audit logging
    
    **→ '4_⬛_PDF_Redaction'**
    """)

st.markdown("---")
st.info("💡 Use the sidebar navigation to switch between tools")