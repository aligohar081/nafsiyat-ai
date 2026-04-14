#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    print("Starting Nafsiyat AI Platform...")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    print("Installing dependencies...")
    subprocess.run([pip_cmd, "install", "-r", "backend/requirements.txt"])
    
    # Start backend server
    print("\nStarting backend server on http://localhost:8000")
    backend_process = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend"
    )
    
    # Start frontend server
    print("Starting frontend server on http://localhost:3000")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd="frontend"
    )
    
    print("\n✅ Nafsiyat AI is running!")
    print(f"📱 Frontend: http://localhost:3000")
    print(f"🔧 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the servers\n")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped.")

if __name__ == "__main__":
    main()