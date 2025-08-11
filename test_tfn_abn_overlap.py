#!/usr/bin/env python3
"""Test that TFN detection doesn't incorrectly match parts of ABNs"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_tfn_abn_test_pdf():
    """Create a test PDF with ABNs and TFNs to test overlap detection"""
    
    filename = "test_tfn_abn_overlap.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "TFN/ABN Overlap Test Document")
    
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    # Test cases with ABNs (should NOT be detected as TFNs)
    c.drawString(100, y_position, "ABNs (should remain intact when only TFN redaction is enabled):")
    y_position -= 30
    
    abn_cases = [
        "ABN: 65 762 770 637",  # Should NOT match last 9 digits as TFN
        "Australian Business Number: 12 345 678 901",
        "A.B.N. 98 765 432 109",
        "Company ABN 51824753556",  # Compact format
    ]
    
    for abn in abn_cases:
        c.drawString(120, y_position, abn)
        y_position -= 25
    
    y_position -= 20
    
    # Test cases with actual TFNs (should be detected)
    c.drawString(100, y_position, "TFNs (should be redacted when TFN redaction is enabled):")
    y_position -= 30
    
    tfn_cases = [
        "TFN: 123 456 789",  # Standard TFN
        "Tax File Number: 987-654-321",
        "Employee TFN 456789123",
        "123 456 789",  # TFN without label
    ]
    
    for tfn in tfn_cases:
        c.drawString(120, y_position, tfn)
        y_position -= 25
    
    y_position -= 20
    
    # Mixed content
    c.drawString(100, y_position, "Mixed content:")
    y_position -= 30
    c.drawString(120, y_position, "Company ABN: 65 762 770 637, Employee TFN: 111 222 333")
    y_position -= 25
    c.drawString(120, y_position, "ABN 12345678901 and TFN 987654321 in same line")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 50, "Test: TFN detection should NOT match the last 9 digits of ABNs")
    
    c.save()
    print(f"Created test PDF: {filename}")
    print("\nTest scenarios:")
    print("1. Enable ONLY TFN redaction")
    print("   - ABNs should remain completely visible")
    print("   - Only actual TFNs should be redacted")
    print("\n2. Enable BOTH TFN and ABN redaction")
    print("   - Both should be properly redacted")
    print("\nThe bug would show as: ABN '65 762 770 637' becomes '65' when only TFN is enabled")

if __name__ == "__main__":
    create_tfn_abn_test_pdf()