#!/bin/bash

# Kill any existing streamlit processes
pkill -f "streamlit run app.py" 2>/dev/null

# Activate virtual environment
source venv/bin/activate

# Start streamlit with proper settings
echo "Starting PDF Combiner app..."
streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --browser.gatherUsageStats false \
    --server.headless true \
    --global.developmentMode false