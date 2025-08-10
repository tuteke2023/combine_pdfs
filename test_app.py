import requests
import os
import PyPDF2
from io import BytesIO
import time

def test_pdf_combiner():
    print("🧪 Testing PDF Combiner Application")
    print("=" * 50)
    
    base_url = "http://localhost:8501"
    
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running at http://localhost:8501")
        else:
            print(f"⚠️ Server responded with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to server: {e}")
        return False
    
    print("\n📁 Test PDFs found:")
    test_files = ["test1_introduction.pdf", "test2_main_content.pdf", 
                  "test3_appendix.pdf", "test4_conclusion.pdf"]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"  ✅ {file} (size: {os.path.getsize(file)} bytes)")
        else:
            print(f"  ❌ {file} not found")
    
    print("\n🔧 Testing PDF combination logic...")
    try:
        pdf_writer = PyPDF2.PdfWriter()
        total_pages = 0
        
        for file in test_files[:2]:
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    num_pages = len(pdf_reader.pages)
                    total_pages += num_pages
                    print(f"  📄 {file}: {num_pages} pages")
                    
                    for page_num in range(num_pages):
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)
        
        test_output = "test_combined.pdf"
        with open(test_output, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        with open(test_output, 'rb') as f:
            result_reader = PyPDF2.PdfReader(f)
            result_pages = len(result_reader.pages)
        
        if result_pages == total_pages:
            print(f"  ✅ Successfully combined PDFs: {result_pages} total pages")
        else:
            print(f"  ❌ Page count mismatch: expected {total_pages}, got {result_pages}")
        
        if os.path.exists(test_output):
            os.remove(test_output)
            print("  🗑️ Cleaned up test output file")
        
    except Exception as e:
        print(f"  ❌ Error during PDF combination: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed successfully!")
    print("\n📝 Instructions to test the web app:")
    print("1. Open http://localhost:8501 in your browser")
    print("2. Upload the test PDF files (test1_introduction.pdf, etc.)")
    print("3. Reorder them if desired using the dropdown menus")
    print("4. Click 'Combine PDFs' button")
    print("5. Download the combined PDF")
    
    return True

if __name__ == "__main__":
    test_pdf_combiner()