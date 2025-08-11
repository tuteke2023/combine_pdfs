#!/bin/bash

echo "Starting PDF Tools Suite..."
echo "================================"

# Kill any existing streamlit processes
pkill -f "streamlit run" 2>/dev/null

# Activate virtual environment
source venv/bin/activate

# Start streamlit
echo ""
echo "📌 Server starting at: http://localhost:8501"
echo "🔑 Password: pdfcombiner123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

streamlit run app.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false \
    --server.headless false