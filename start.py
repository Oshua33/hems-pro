import os
import sys
import subprocess
import time
import webbrowser

# Set timezone
os.environ["TZ"] = "Africa/Lagos"

# Determine base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Python executable paths
PYTHON_VENV = os.path.join(BASE_DIR, "env", "Scripts", "python.exe")
PYTHON_EMBED = os.path.join(BASE_DIR, "python", "python.exe")

# Choose correct Python executable
if os.path.exists(PYTHON_VENV):
    PYTHON_EXECUTABLE = PYTHON_VENV
elif os.path.exists(PYTHON_EMBED):
    PYTHON_EXECUTABLE = PYTHON_EMBED
else:
    print("❌ Error: No valid Python environment found.")
    sys.exit(1)

def start_backend():
    """Start FastAPI backend which serves both API and React UI"""
    command = [
        PYTHON_EXECUTABLE, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info",
        "--no-access-log"  # <-- This disables the repeating INFO access log
    ]
    return subprocess.Popen(command, cwd=BASE_DIR)


def open_browser():
    """Open default browser to React UI"""
    time.sleep(3)  # Wait for backend to start
    webbrowser.open("http://127.0.0.1:8000/web/")

if __name__ == "__main__":
    print("🚀 Starting backend...")
    backend_proc = start_backend()
    open_browser()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend_proc.terminate()
