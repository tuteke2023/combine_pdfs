# TTA PDF Tool Suite

A comprehensive Streamlit web application with multiple PDF tools including PDF combiner, encryptor, and signature tool - all with password protection.

## Features

### 🏠 Main Features
- 🔒 **Password Protected Access**: Secure login system for all tools
- 📑 **Multi-Page App**: Navigate between different PDF tools
- 🚪 **Session Management**: Login/logout functionality

### 📄 PDF Combiner
- 📥 **Drag & Drop Upload**: Drag PDF files directly onto the upload area
- 👁️ **PDF Preview**: View first page text content and file information
- 📊 **File Details**: See page count and file size for each PDF
- 🔄 **Visual Reordering**: Easy file reordering with grid layout display
- 📈 **Progress Tracking**: Real-time progress bar during combination

### 🔐 PDF Encryptor
- 🔑 **Automatic Password Generation**: Cryptographically secure random passwords
- 🛡️ **128-bit AES Encryption**: Strong PDF encryption
- 📦 **Bulk Processing**: Encrypt multiple PDFs at once
- 📝 **Password Management**: Download password list for encrypted files
- 🗂️ **ZIP Download**: Download all encrypted files and passwords in one ZIP

### ✍️ PDF Signature
- 📸 **Flexible Signature Input**: Upload signature image or draw digitally
- 📍 **Interactive Positioning**: Click on PDF preview to position signature
- 📅 **Date Stamp**: Optional automatic date addition below signature
- 📑 **Multi-Page Support**: Choose which page to sign
- 👁️ **Live Preview**: See exactly where signature will appear before applying

## Installation

### Prerequisites

No system dependencies required! The app now uses PyMuPDF for PDF preview functionality, which works entirely within the Python environment.

### Setup

1. Clone the repository:
```bash
git clone git@github.com:tuteke2023/tta-pdf-tool-suite.git
cd tta-pdf-tool-suite
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install streamlit PyPDF2 reportlab
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to http://localhost:8501

3. Upload PDF files using the file uploader

4. Reorder files using the dropdown menus if needed

5. Click "Combine PDFs" to merge them

6. Download your combined PDF file

## Files

- `app.py` - Main Streamlit application
- `generate_test_pdfs.py` - Script to generate test PDF files
- `test_app.py` - Testing script for the application
- `start_app.sh` - Shell script to start the application

## Requirements

- Python 3.8+
- streamlit
- PyPDF2
- reportlab (for generating test PDFs)

## License

MIT