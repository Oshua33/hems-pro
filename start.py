import os
import sys
import subprocess
import time
from datetime import datetime

# Set Africa/Lagos as the default timezone
os.environ["TZ"] = "Africa/Lagos"

# Determine BASE_DIR dynamically
if getattr(sys, 'frozen', False):  # Running from an Inno Setup installation
    BASE_DIR = os.path.dirname(sys.executable)  # Use the directory where the EXE is located
else:  # Running from the development environment
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths for Python environments
PYTHON_VENV = os.path.join(BASE_DIR, "env", "Scripts", "python.exe")  # Virtual environment (Development)
PYTHON_EMBED = os.path.join(BASE_DIR, "python", "python.exe")  # Embedded Python (Installer)

# Determine which Python executable to use
if os.path.exists(PYTHON_VENV):
    PYTHON_EXECUTABLE = PYTHON_VENV
elif os.path.exists(PYTHON_EMBED):
    PYTHON_EXECUTABLE = PYTHON_EMBED
else:
    print("Error: No valid Python environment found.")
    sys.exit(1)

def start_backend():
    """Starts the FastAPI backend using the appropriate Python environment."""
    backend_script = os.path.join(BASE_DIR, "app", "main.py")

    if not os.path.exists(backend_script):
        print(f"Error: Backend script not found at {backend_script}")
        sys.exit(1)

    with open(os.path.join(BASE_DIR, "error.log"), "w") as log_file:
        process = subprocess.Popen([PYTHON_EXECUTABLE, "-m", "app.main"], cwd=BASE_DIR, stderr=log_file)
    
    return process  # Keep running in the background

def start_frontend():
    """Starts the Tkinter frontend using the appropriate Python environment."""
    frontend_script = os.path.join(BASE_DIR, "frontend", "main.py")

    if not os.path.exists(frontend_script):
        print(f"Error: Frontend script not found at {frontend_script}")
        sys.exit(1)

    subprocess.Popen([PYTHON_EXECUTABLE, frontend_script], cwd=BASE_DIR)

if __name__ == "__main__":
    backend_process = start_backend()
    start_frontend()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend_process.terminate()
