# PDF Tools Suite

A comprehensive Streamlit web application with multiple PDF tools including a PDF combiner and PDF encryptor with password protection.

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

## Installation

1. Clone the repository:
```bash
git clone git@github.com:tuteke2023/combine_pdfs.git
cd combine_pdfs
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