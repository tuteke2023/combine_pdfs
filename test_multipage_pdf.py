#!/usr/bin/env python3
"""Generate a multi-page test PDF for testing the Page Manager"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

def create_multipage_test_pdf():
    """Create a test PDF with multiple pages for testing page management"""
    
    filename = "test_multipage_document.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Create 10 test pages with different content
    test_pages = [
        ("Cover Page", "Annual Report 2024", colors.navy),
        ("Table of Contents", "1. Executive Summary\n2. Financial Overview\n3. Operations Report", colors.black),
        ("Executive Summary", "Key achievements and highlights for the year", colors.darkgreen),
        ("Financial Overview", "Revenue: $1.2M\nExpenses: $800K\nProfit: $400K", colors.darkblue),
        ("Operations Report", "Efficiency increased by 25%", colors.purple),
        ("Blank Page", "[Intentionally left blank]", colors.gray),
        ("Marketing Analysis", "Market share grew by 15%", colors.orange),
        ("HR Report", "Staff count: 45 employees", colors.brown),
        ("Blank Page 2", "[This page intentionally left blank]", colors.gray),
        ("Appendix", "Additional supporting documents", colors.darkred),
    ]
    
    for page_num, (title, content, color) in enumerate(test_pages, 1):
        # Page header
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, height - 100, title)
        
        # Page number
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(width - 100, 50, f"Page {page_num}")
        
        # Content
        c.setFont("Helvetica", 14)
        y_position = height - 150
        for line in content.split('\n'):
            c.drawString(100, y_position, line)
            y_position -= 25
        
        # Visual marker for easy identification
        c.setFillColor(color)
        c.rect(50, height - 50, 20, 20, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(54, height - 45, str(page_num))
        
        # Add page
        c.showPage()
    
    c.save()
    print(f"Created test PDF: {filename}")
    print(f"Total pages: {len(test_pages)}")
    print("\nTest scenarios for Page Manager:")
    print("1. Preview all pages visually")
    print("2. Delete blank pages (pages 6 and 9)")
    print("3. Reorder to put Appendix after Table of Contents")
    print("4. Extract only Financial and Operations reports (pages 4-5)")
    print("5. Reverse entire document order")

if __name__ == "__main__":
    create_multipage_test_pdf()