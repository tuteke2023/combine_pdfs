import streamlit as st
import hmac

st.set_page_config(
    page_title="PDF Tools Suite", 
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

    st.title("🔐 PDF Tools Suite - Login")
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
st.title("📄 PDF Tools Suite")
st.markdown("Welcome to the PDF Tools Suite! Choose a tool from the sidebar to get started.")

col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🚪 Logout", type="secondary"):
        st.session_state["password_correct"] = False
        st.rerun()

st.markdown("---")

# Display available tools
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔀 PDF Combiner
    Combine multiple PDF files into a single document with:
    - Drag & drop file upload
    - Preview and reorder files
    - Download combined PDF
    
    **→ Select '1_📄_PDF_Combiner' from the sidebar**
    """)

with col2:
    st.markdown("""
    ### 🔒 PDF Encryptor
    Protect your PDF files with password encryption:
    - Upload single or multiple PDFs
    - Automatic secure password generation
    - Download encrypted PDFs with passwords
    
    **→ Select '2_🔒_PDF_Encryptor' from the sidebar**
    """)

st.markdown("---")
st.info("💡 Use the sidebar navigation to switch between tools")