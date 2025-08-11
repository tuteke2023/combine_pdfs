#!/usr/bin/env python3
"""Generate a test PDF with sensitive data for testing redaction tool"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_test_pdf_with_sensitive_data():
    """Create a test PDF with TFN, ABN, and other sensitive data"""
    
    filename = "test_sensitive_data.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Employee Tax Information")
    
    # Sample employee data with TFN
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    employees = [
        ("John Smith", "123 456 789", "john.smith@example.com", "0412 345 678"),
        ("Jane Doe", "987-654-321", "jane.doe@company.com", "(02) 9876 5432"),
        ("Bob Johnson", "456789123", "bob@email.com", "+61 400 123 456"),
    ]
    
    for name, tfn, email, phone in employees:
        c.drawString(100, y_position, f"Name: {name}")
        y_position -= 20
        c.drawString(100, y_position, f"Tax File Number: {tfn}")
        y_position -= 20
        c.drawString(100, y_position, f"Email: {email}")
        y_position -= 20
        c.drawString(100, y_position, f"Phone: {phone}")
        y_position -= 40
    
    # Company information with ABN
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "Company Information")
    y_position -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(100, y_position, "Company: TTA Accounting Services")
    y_position -= 20
    c.drawString(100, y_position, "ABN: 12 345 678 901")
    y_position -= 20
    c.drawString(100, y_position, "Business Phone: 1300 123 456")
    y_position -= 40
    
    # Additional sensitive info
    c.drawString(100, y_position, "Additional Information:")
    y_position -= 20
    c.drawString(100, y_position, "TFN for trust: 111 222 333")
    y_position -= 20
    c.drawString(100, y_position, "Australian Business Number (ABN): 98765432109")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 50, "Confidential - Contains sensitive tax information")
    
    c.save()
    print(f"Created test PDF: {filename}")
    print("\nTest data includes:")
    print("- TFNs in various formats (XXX XXX XXX, XXX-XXX-XXX, XXXXXXXXX)")
    print("- ABNs in different formats")
    print("- Email addresses")
    print("- Phone numbers (mobile and landline)")
    print("\nUse this file to test the PDF Redaction tool")

if __name__ == "__main__":
    create_test_pdf_with_sensitive_data()