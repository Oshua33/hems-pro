import os
import sys
import subprocess
import time
import webbrowser
import psutil
import socket

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


def get_preferred_ip():
    """
    Prefer Ethernet IP > Wi-Fi IP > fallback to 127.0.0.1
    """
    ip_priority = {
        "Ethernet": None,
        "Wi-Fi": None,
    }

    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("169.254"):
                if "Ethernet" in interface and not ip_priority["Ethernet"]:
                    ip_priority["Ethernet"] = addr.address
                elif "Wi-Fi" in interface and not ip_priority["Wi-Fi"]:
                    ip_priority["Wi-Fi"] = addr.address

    return ip_priority["Ethernet"] or ip_priority["Wi-Fi"] or "127.0.0.1"


def start_backend():
    """Start FastAPI backend which serves both API and React UI"""
    command = [
        PYTHON_EXECUTABLE, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info",
        "--no-access-log"
    ]
    return subprocess.Popen(command, cwd=BASE_DIR)


def open_browser():
    """Open browser to the preferred IP"""
    time.sleep(3)  # Wait for backend to start
    ip = get_preferred_ip()
    print(f"🌐 Opening browser at http://{ip}:8000/web/")
    webbrowser.open(f"http://{ip}:8000/web/")

if __name__ == "__main__":
    print("🚀 Starting backend...")
    backend_proc = start_backend()
    open_browser()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend_proc.terminate()
