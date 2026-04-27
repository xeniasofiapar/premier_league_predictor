import subprocess
import webbrowser
import time
import os
import sys

# Set environment variables to suppress warnings
os.environ["STREAMLIT_LOGGER_LEVEL"] = "error"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["PYTHONWARNINGS"] = "ignore"

# Start Streamlit
print("🚀 Starting Streamlit app...\n")
proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app_advanced.py", "--logger.level=error"],
    cwd=os.path.dirname(os.path.abspath(__file__))
)

# Wait for the app to start
time.sleep(3)

# Open browser automatically
print("🌐 Opening browser...\n")
webbrowser.open("http://localhost:8501")

# Keep the process running
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    print("\n✅ App closed.")