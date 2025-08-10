#!/bin/bash

# Kill any existing streamlit processes
pkill -f "streamlit run" 2>/dev/null

# Activate virtual environment
source venv/bin/activate

# Start streamlit
echo "Starting PDF Combiner on http://localhost:8501"
echo "Password: pdfcombiner123"
echo "Press Ctrl+C to stop"

streamlit run app.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false