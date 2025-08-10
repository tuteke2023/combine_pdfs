from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import random

def create_test_pdf(filename, title, content, num_pages=2):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#48BFE3"]
    color = random.choice(colors)
    
    for page in range(num_pages):
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(HexColor(color))
        c.drawString(100, height - 100, title)
        
        c.setFont("Helvetica", 14)
        c.setFillColor(HexColor("#333333"))
        c.drawString(100, height - 140, f"Page {page + 1} of {num_pages}")
        
        c.setFont("Helvetica", 12)
        y_position = height - 180
        for line in content:
            c.drawString(100, y_position, line)
            y_position -= 20
        
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#999999"))
        c.drawString(100, 50, f"Test PDF - {filename} - Page {page + 1}")
        
        c.showPage()
    
    c.save()
    print(f"Created: {filename}")

test_pdfs = [
    {
        "filename": "test1_introduction.pdf",
        "title": "1. Introduction Document",
        "content": [
            "This is the introduction section of our combined document.",
            "It contains important preliminary information.",
            "This document will be the first in the combined PDF.",
            "",
            "Key Points:",
            "• Welcome message",
            "• Overview of contents",
            "• Purpose statement"
        ],
        "pages": 2
    },
    {
        "filename": "test2_main_content.pdf",
        "title": "2. Main Content",
        "content": [
            "This is the main content section.",
            "It contains the core information of our document.",
            "",
            "Topics Covered:",
            "• Primary concepts",
            "• Detailed explanations",
            "• Examples and illustrations",
            "• Best practices"
        ],
        "pages": 3
    },
    {
        "filename": "test3_appendix.pdf",
        "title": "3. Appendix",
        "content": [
            "This is the appendix section.",
            "Additional reference materials are included here.",
            "",
            "Contents:",
            "• Glossary of terms",
            "• References",
            "• Additional resources",
            "• Contact information"
        ],
        "pages": 2
    },
    {
        "filename": "test4_conclusion.pdf",
        "title": "4. Conclusion",
        "content": [
            "This is the conclusion section.",
            "Summary and final thoughts are presented here.",
            "",
            "Final Notes:",
            "• Key takeaways",
            "• Next steps",
            "• Thank you message",
            "• Future directions"
        ],
        "pages": 1
    }
]

for pdf in test_pdfs:
    create_test_pdf(
        pdf["filename"],
        pdf["title"],
        pdf["content"],
        pdf["pages"]
    )

print("\n✅ All test PDFs have been generated successfully!")
print("You can now use these files to test the PDF combiner application.")