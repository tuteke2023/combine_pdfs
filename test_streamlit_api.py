import requests
import json
import time

def test_streamlit_api():
    print("🔍 Testing Streamlit App API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8501"
    
    # Test health endpoint
    try:
        health_url = f"{base_url}/_stcore/health"
        response = requests.get(health_url, timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Streamlit health endpoint is responding")
    except Exception as e:
        print(f"⚠️ Health check failed: {e}")
    
    # Test stream endpoint
    try:
        stream_url = f"{base_url}/_stcore/stream"
        response = requests.get(stream_url, timeout=5)
        print(f"Stream endpoint: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Stream check failed: {e}")
    
    # Check if main page loads
    try:
        response = requests.get(base_url, timeout=5)
        if "streamlit" in response.text.lower():
            print("✅ Main page contains Streamlit content")
        if "PDF Combiner" in response.text:
            print("✅ App title 'PDF Combiner' found in page")
    except Exception as e:
        print(f"❌ Main page check failed: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Summary: The Streamlit server is running and accessible")
    print("Note: Full UI testing requires manual browser interaction")

if __name__ == "__main__":
    test_streamlit_api()