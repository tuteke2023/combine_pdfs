import streamlit as st
import re
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os
try:
    import fitz  # PyMuPDF for text extraction and rendering
    PYMUPDF_AVAILABLE = True
except:
    PYMUPDF_AVAILABLE = False
from PIL import Image, ImageDraw
import zipfile
from datetime import datetime

st.set_page_config(page_title="PDF Redaction", page_icon="⬛", layout="wide")

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first")
    st.stop()

st.title("⬛ PDF Redaction Tool")
st.markdown("Automatically detect and redact sensitive information like TFNs, ABNs, and other confidential data from PDF documents.")

# Warning message
st.warning("⚠️ **Important**: Redaction is permanent and cannot be undone. Always keep original copies of your documents.")

# Initialize session state
if 'redaction_patterns' not in st.session_state:
    st.session_state.redaction_patterns = {
        'tfn': True,
        'abn': False,
        'email': False,
        'phone': False,
        'custom': False
    }
if 'detected_items' not in st.session_state:
    st.session_state.detected_items = []
if 'manual_redactions' not in st.session_state:
    st.session_state.manual_redactions = []

def detect_tfn(text):
    """Detect potential TFN patterns in text"""
    patterns = []
    
    # TFN patterns: 9 digits in various formats
    tfn_patterns = [
        r'\b\d{3}[\s-]?\d{3}[\s-]?\d{3}\b',  # XXX XXX XXX or XXX-XXX-XXX
        r'\b\d{9}\b',  # XXXXXXXXX
    ]
    
    # Also look for context clues
    context_patterns = [
        r'(?i)(?:tfn|tax\s*file\s*number|tax\s*file\s*no)[:\s]*(\d{3}[\s-]?\d{3}[\s-]?\d{3}|\d{9})',
    ]
    
    found_items = []
    seen_positions = set()  # Track positions to avoid duplicates
    
    for pattern in tfn_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Validate it looks like a TFN (basic validation)
            digits = re.sub(r'\D', '', match.group())
            if len(digits) == 9 and match.start() not in seen_positions:
                found_items.append({
                    'type': 'TFN',
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'digits': digits  # Store normalized digits for better matching
                })
                seen_positions.add(match.start())
    
    for pattern in context_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            if match.start() not in seen_positions:
                digits = re.sub(r'\D', '', match.group())
                found_items.append({
                    'type': 'TFN (with context)',
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'digits': digits
                })
                seen_positions.add(match.start())
    
    return found_items

def detect_abn(text):
    """Detect potential ABN patterns in text"""
    patterns = []
    
    # ABN patterns: 11 digits in various formats
    # More flexible patterns to catch different spacing
    abn_patterns = [
        r'\b\d{2}\s+\d{3}\s+\d{3}\s+\d{3}\b',  # XX XXX XXX XXX (with spaces)
        r'\b\d{2}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b',  # XX XXX XXX XXX or XX-XXX-XXX-XXX
        r'\b\d{11}\b',  # XXXXXXXXXXX
    ]
    
    context_patterns = [
        r'(?i)(?:abn|australian\s*business\s*number|a\.b\.n\.)[:\s]*(\d{2}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}|\d{11})',
    ]
    
    found_items = []
    seen_positions = set()  # Track positions to avoid duplicates
    
    for pattern in abn_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            digits = re.sub(r'\D', '', match.group())
            if len(digits) == 11:
                # Check if we've already found an ABN at this position
                if match.start() not in seen_positions:
                    found_items.append({
                        'type': 'ABN',
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'digits': digits  # Store normalized digits for better matching
                    })
                    seen_positions.add(match.start())
    
    for pattern in context_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            if match.start() not in seen_positions:
                found_items.append({
                    'type': 'ABN (with context)',
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'digits': re.sub(r'\D', '', match.group())
                })
                seen_positions.add(match.start())
    
    return found_items

def detect_email(text):
    """Detect email addresses in text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.finditer(email_pattern, text)
    
    found_items = []
    for match in matches:
        found_items.append({
            'type': 'Email',
            'text': match.group(),
            'start': match.start(),
            'end': match.end()
        })
    
    return found_items

def detect_phone(text):
    """Detect Australian phone numbers in text"""
    phone_patterns = [
        r'(?:\+61|0)[2-9]\d{8}',  # Australian mobile/landline
        r'\(0[2-9]\)\s*\d{4}[\s-]?\d{4}',  # (0X) XXXX XXXX
        r'0[2-9][\s-]?\d{4}[\s-]?\d{4}',  # 0X XXXX XXXX
    ]
    
    found_items = []
    for pattern in phone_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            found_items.append({
                'type': 'Phone',
                'text': match.group(),
                'start': match.start(),
                'end': match.end()
            })
    
    return found_items

def detect_custom_pattern(text, pattern_str):
    """Detect custom regex pattern in text"""
    try:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = pattern.finditer(text)
        
        found_items = []
        for match in matches:
            found_items.append({
                'type': 'Custom',
                'text': match.group(),
                'start': match.start(),
                'end': match.end()
            })
        return found_items
    except re.error:
        return []

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF using PyMuPDF"""
    if not PYMUPDF_AVAILABLE:
        st.error("PyMuPDF is required for text extraction")
        return []
    
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)
    
    try:
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        pages_text = []
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            text = page.get_text()
            pages_text.append(text)
        
        pdf_doc.close()
        return pages_text
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return []

def create_redacted_pdf(pdf_file, redaction_items, pages_to_redact=None):
    """Create a redacted version of the PDF"""
    if not PYMUPDF_AVAILABLE:
        st.error("PyMuPDF is required for redaction")
        return None
    
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)
    
    try:
        # Open PDF with PyMuPDF
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Group redaction items by page
        redactions_by_page = {}
        for item in redaction_items:
            page_num = item.get('page', 0)
            if pages_to_redact is None or page_num in pages_to_redact:
                if page_num not in redactions_by_page:
                    redactions_by_page[page_num] = []
                redactions_by_page[page_num].append(item)
        
        # Apply redactions
        for page_num, items in redactions_by_page.items():
            if page_num < len(pdf_doc):
                page = pdf_doc[page_num]
                
                for item in items:
                    # Search for text and get its location
                    text_instances = page.search_for(item['text'])
                    
                    # If exact match doesn't work, try searching for normalized digits
                    if not text_instances and 'digits' in item:
                        # For ABN/TFN, try to find the digits in various formats
                        digits = item['digits']
                        
                        # Try different ABN formats if it's 11 digits
                        if len(digits) == 11:
                            # Try XX XXX XXX XXX format
                            formatted = f"{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
                            text_instances = page.search_for(formatted)
                            
                            if not text_instances:
                                # Try XXXXXXXXXXX format
                                text_instances = page.search_for(digits)
                            
                            if not text_instances:
                                # Try XX-XXX-XXX-XXX format
                                formatted = f"{digits[:2]}-{digits[2:5]}-{digits[5:8]}-{digits[8:]}"
                                text_instances = page.search_for(formatted)
                        
                        # Try different TFN formats if it's 9 digits
                        elif len(digits) == 9:
                            # Try XXX XXX XXX format
                            formatted = f"{digits[:3]} {digits[3:6]} {digits[6:]}"
                            text_instances = page.search_for(formatted)
                            
                            if not text_instances:
                                # Try XXXXXXXXX format
                                text_instances = page.search_for(digits)
                            
                            if not text_instances:
                                # Try XXX-XXX-XXX format
                                formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                                text_instances = page.search_for(formatted)
                    
                    # Add redaction annotation for each instance
                    for inst in text_instances:
                        page.add_redact_annot(inst)
                
                # Apply the redactions (this makes them permanent)
                page.apply_redactions()
        
        # Save to bytes
        output = io.BytesIO()
        pdf_doc.save(output)
        pdf_doc.close()
        
        output.seek(0)
        return output
        
    except Exception as e:
        st.error(f"Error creating redacted PDF: {str(e)}")
        return None

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose PDF file(s) to redact",
        type="pdf",
        accept_multiple_files=True,
        help="Upload one or more PDF files for redaction"
    )
    
    if uploaded_file:
        # Handle multiple files
        files = uploaded_file if isinstance(uploaded_file, list) else [uploaded_file]
        
        st.header("🔍 Detection Settings")
        
        # Pattern selection
        st.subheader("Select patterns to detect:")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.redaction_patterns['tfn'] = st.checkbox(
                "🆔 TFN (Tax File Numbers)",
                value=st.session_state.redaction_patterns['tfn'],
                help="Detects 9-digit tax file numbers"
            )
            st.session_state.redaction_patterns['email'] = st.checkbox(
                "📧 Email Addresses",
                value=st.session_state.redaction_patterns['email']
            )
        
        with col_b:
            st.session_state.redaction_patterns['abn'] = st.checkbox(
                "🏢 ABN (Australian Business Numbers)",
                value=st.session_state.redaction_patterns['abn'],
                help="Detects 11-digit business numbers"
            )
            st.session_state.redaction_patterns['phone'] = st.checkbox(
                "📱 Phone Numbers",
                value=st.session_state.redaction_patterns['phone'],
                help="Detects Australian phone numbers"
            )
        
        # Custom pattern
        st.session_state.redaction_patterns['custom'] = st.checkbox(
            "🔧 Custom Pattern (Regex)",
            value=st.session_state.redaction_patterns['custom']
        )
        
        custom_pattern = None
        if st.session_state.redaction_patterns['custom']:
            custom_pattern = st.text_input(
                "Enter regex pattern:",
                placeholder=r"e.g., \b\d{4}\s\d{4}\s\d{4}\s\d{4}\b for credit cards",
                help="Enter a regular expression pattern to match"
            )
        
        # Scan button
        if st.button("🔍 Scan for Sensitive Data", type="primary", use_container_width=True):
            with st.spinner("Scanning PDF(s) for sensitive information..."):
                all_detections = []
                
                for file_idx, pdf_file in enumerate(files):
                    pdf_file.seek(0)
                    pages_text = extract_text_from_pdf(pdf_file)
                    
                    file_detections = []
                    for page_num, text in enumerate(pages_text):
                        page_detections = []
                        
                        if st.session_state.redaction_patterns['tfn']:
                            tfns = detect_tfn(text)
                            for item in tfns:
                                item['page'] = page_num
                                item['file'] = pdf_file.name
                                item['file_idx'] = file_idx
                            page_detections.extend(tfns)
                        
                        if st.session_state.redaction_patterns['abn']:
                            abns = detect_abn(text)
                            for item in abns:
                                item['page'] = page_num
                                item['file'] = pdf_file.name
                                item['file_idx'] = file_idx
                            page_detections.extend(abns)
                        
                        if st.session_state.redaction_patterns['email']:
                            emails = detect_email(text)
                            for item in emails:
                                item['page'] = page_num
                                item['file'] = pdf_file.name
                                item['file_idx'] = file_idx
                            page_detections.extend(emails)
                        
                        if st.session_state.redaction_patterns['phone']:
                            phones = detect_phone(text)
                            for item in phones:
                                item['page'] = page_num
                                item['file'] = pdf_file.name
                                item['file_idx'] = file_idx
                            page_detections.extend(phones)
                        
                        if st.session_state.redaction_patterns['custom'] and custom_pattern:
                            custom_items = detect_custom_pattern(text, custom_pattern)
                            for item in custom_items:
                                item['page'] = page_num
                                item['file'] = pdf_file.name
                                item['file_idx'] = file_idx
                            page_detections.extend(custom_items)
                        
                        file_detections.extend(page_detections)
                    
                    # Deduplicate detections for this file
                    # Group by page, type, and normalized text to remove duplicates
                    seen = set()
                    unique_detections = []
                    for item in file_detections:
                        # Normalize the text (remove spaces/dashes for comparison)
                        normalized = re.sub(r'[\s\-]', '', item['text'])
                        key = (item['page'], item['type'].split(' ')[0], normalized)  # Use base type for grouping
                        if key not in seen:
                            seen.add(key)
                            unique_detections.append(item)
                    
                    all_detections.extend(unique_detections)
                
                st.session_state.detected_items = all_detections
                
                # Count unique sensitive values (not instances)
                unique_values = set()
                for item in all_detections:
                    normalized = re.sub(r'[\s\-]', '', item['text'])
                    unique_values.add(normalized)
                
                if all_detections:
                    if len(unique_values) != len(all_detections):
                        st.success(f"✅ Found {len(unique_values)} unique sensitive items across {len(all_detections)} locations")
                    else:
                        st.success(f"✅ Found {len(all_detections)} items to redact")
                else:
                    st.info("No sensitive data detected with selected patterns")

with col2:
    if uploaded_file and st.session_state.detected_items:
        st.header("📋 Detected Items")
        
        # Group by file
        files_dict = {}
        for item in st.session_state.detected_items:
            file_name = item['file']
            if file_name not in files_dict:
                files_dict[file_name] = []
            files_dict[file_name].append(item)
        
        # Display detected items
        for file_name, items in files_dict.items():
            # Count unique values for this file
            unique_in_file = set()
            for item in items:
                normalized = re.sub(r'[\s\-]', '', item['text'])
                unique_in_file.add(normalized)
            
            with st.expander(f"📄 {file_name} ({len(unique_in_file)} unique items, {len(items)} total locations)", expanded=True):
                # Group by base type (without context suffix)
                by_type = {}
                for item in items:
                    # Group TFN and TFN (with context) together
                    base_type = item['type'].replace(' (with context)', '')
                    if base_type not in by_type:
                        by_type[base_type] = {}
                    
                    # Use normalized text as key to group duplicates
                    normalized = re.sub(r'[\s\-]', '', item['text'])
                    if normalized not in by_type[base_type]:
                        by_type[base_type][normalized] = []
                    by_type[base_type][normalized].append(item)
                
                for type_name, type_values in by_type.items():
                    st.write(f"**{type_name}** ({len(type_values)} unique):")
                    for normalized_text, instances in list(type_values.items())[:5]:  # Show first 5 unique values
                        # Show the original text from first instance
                        display_text = instances[0]['text']
                        pages = sorted(set(item['page'] + 1 for item in instances))
                        if len(pages) == 1:
                            st.write(f"• Page {pages[0]}: `{display_text}`")
                        else:
                            st.write(f"• Pages {', '.join(map(str, pages))}: `{display_text}`")
                    if len(type_values) > 5:
                        st.write(f"... and {len(type_values) - 5} more unique values")
        
        st.markdown("---")
        
        # Redaction confirmation
        st.warning("⚠️ **Final Confirmation**: Redaction is permanent!")
        
        col_confirm = st.columns([2, 1])
        with col_confirm[0]:
            confirm = st.checkbox("I understand that redaction is irreversible")
        
        with col_confirm[1]:
            if st.button("⬛ Apply Redactions", type="primary", disabled=not confirm):
                with st.spinner("Applying redactions..."):
                    files = uploaded_file if isinstance(uploaded_file, list) else [uploaded_file]
                    
                    if len(files) == 1:
                        # Single file - direct download
                        pdf_file = files[0]
                        pdf_file.seek(0)
                        
                        # Filter detections for this file
                        file_items = [item for item in st.session_state.detected_items 
                                    if item['file'] == pdf_file.name]
                        
                        redacted_pdf = create_redacted_pdf(pdf_file, file_items)
                        
                        if redacted_pdf:
                            st.success("✅ Redaction complete!")
                            
                            # Generate audit log
                            audit_log = f"Redaction Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            audit_log += f"File: {pdf_file.name}\n"
                            audit_log += f"Total items redacted: {len(file_items)}\n\n"
                            
                            by_type = {}
                            for item in file_items:
                                if item['type'] not in by_type:
                                    by_type[item['type']] = 0
                                by_type[item['type']] += 1
                            
                            for type_name, count in by_type.items():
                                audit_log += f"- {type_name}: {count} items\n"
                            
                            # Download buttons
                            col_dl1, col_dl2 = st.columns(2)
                            with col_dl1:
                                st.download_button(
                                    "📥 Download Redacted PDF",
                                    data=redacted_pdf.getvalue(),
                                    file_name=pdf_file.name.replace('.pdf', '_REDACTED.pdf'),
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            with col_dl2:
                                st.download_button(
                                    "📋 Download Audit Log",
                                    data=audit_log,
                                    file_name=pdf_file.name.replace('.pdf', '_redaction_log.txt'),
                                    mime="text/plain",
                                    use_container_width=True
                                )
                    else:
                        # Multiple files - create ZIP
                        zip_buffer = io.BytesIO()
                        audit_logs = []
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for pdf_file in files:
                                pdf_file.seek(0)
                                
                                # Filter detections for this file
                                file_items = [item for item in st.session_state.detected_items 
                                            if item['file'] == pdf_file.name]
                                
                                if file_items:
                                    redacted_pdf = create_redacted_pdf(pdf_file, file_items)
                                    
                                    if redacted_pdf:
                                        # Add redacted PDF to ZIP
                                        redacted_name = pdf_file.name.replace('.pdf', '_REDACTED.pdf')
                                        zip_file.writestr(redacted_name, redacted_pdf.getvalue())
                                        
                                        # Create audit log for this file
                                        audit_log = f"File: {pdf_file.name}\n"
                                        audit_log += f"Total items redacted: {len(file_items)}\n"
                                        
                                        by_type = {}
                                        for item in file_items:
                                            if item['type'] not in by_type:
                                                by_type[item['type']] = 0
                                            by_type[item['type']] += 1
                                        
                                        for type_name, count in by_type.items():
                                            audit_log += f"- {type_name}: {count} items\n"
                                        
                                        audit_logs.append(audit_log)
                            
                            # Add combined audit log
                            full_audit = f"Redaction Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            full_audit += f"Total files processed: {len(files)}\n\n"
                            full_audit += "\n---\n".join(audit_logs)
                            zip_file.writestr("redaction_log.txt", full_audit)
                        
                        zip_buffer.seek(0)
                        
                        st.success(f"✅ Redacted {len(files)} files!")
                        st.download_button(
                            "📥 Download All (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"redacted_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
    
    elif uploaded_file and not st.session_state.detected_items:
        st.info("👈 Configure detection settings and click 'Scan for Sensitive Data' to begin")

# Instructions
st.markdown("---")
with st.expander("📖 How to Use", expanded=False):
    st.markdown("""
    ### 🔍 PDF Redaction Tool Guide
    
    **Purpose**: Permanently remove sensitive information from PDF documents
    
    **Steps**:
    1. **Upload** one or more PDF files
    2. **Select** the types of sensitive data to detect:
       - TFN (Tax File Numbers)
       - ABN (Australian Business Numbers)
       - Email addresses
       - Phone numbers
       - Custom patterns (using regex)
    3. **Scan** the documents to find sensitive data
    4. **Review** the detected items
    5. **Confirm** and apply redactions
    6. **Download** the redacted PDFs and audit log
    
    **Important Notes**:
    - ⚠️ Redaction is **permanent** and cannot be undone
    - 📁 Always keep backup copies of original documents
    - 📋 An audit log is generated for compliance
    - 🔒 Redacted areas are completely removed, not just covered
    
    **Pattern Examples**:
    - TFN: 123 456 789 or 123-456-789
    - ABN: 12 345 678 901
    - Custom regex for credit cards: `\\b\\d{4}\\s\\d{4}\\s\\d{4}\\s\\d{4}\\b`
    """)

with st.expander("⚖️ Legal & Compliance", expanded=False):
    st.markdown("""
    ### Compliance Information
    
    This tool helps meet privacy requirements including:
    - 🇦🇺 Australian Privacy Act 1988
    - 📊 GDPR (where applicable)
    - 🏢 Professional accounting standards
    
    **Best Practices**:
    - Document all redactions in audit logs
    - Maintain unredacted originals in secure storage
    - Verify redactions before sharing documents
    - Use appropriate retention policies
    """)