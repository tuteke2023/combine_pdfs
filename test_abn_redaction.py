#!/usr/bin/env python3
"""Generate a test PDF with various ABN formats for testing redaction"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_abn_test_pdf():
    """Create a test PDF with ABNs in various formats"""
    
    filename = "test_abn_formats.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "ABN Format Test Document")
    
    # Various ABN formats
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    test_cases = [
        ("Standard Format:", "65 762 770 637"),
        ("No Spaces:", "65762770637"),
        ("Dashes:", "65-762-770-637"),
        ("Mixed Spacing:", "65  762  770  637"),
        ("With Label:", "ABN: 65 762 770 637"),
        ("Full Label:", "Australian Business Number: 98 765 432 109"),
        ("A.B.N. Format:", "A.B.N. 12 345 678 901"),
        ("Different ABN:", "51 824 753 556"),
    ]
    
    for label, abn in test_cases:
        c.drawString(100, y_position, label)
        y_position -= 20
        c.drawString(120, y_position, abn)
        y_position -= 30
    
    # Additional text to test partial matches
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "Business Details")
    y_position -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(100, y_position, "Our ABN is 65 762 770 637 for tax purposes.")
    y_position -= 20
    c.drawString(100, y_position, "Trading as: Company Pty Ltd (ABN 65762770637)")
    y_position -= 20
    c.drawString(100, y_position, "Invoice ABN: 65-762-770-637")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 50, "Test document for ABN redaction verification")
    
    c.save()
    print(f"Created test PDF: {filename}")
    print("\nABN formats included:")
    for label, abn in test_cases:
        print(f"  - {label} {abn}")
    print("\nUse this file to verify ABN redaction works for all formats")

if __name__ == "__main__":
    create_abn_test_pdf()