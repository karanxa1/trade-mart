import subprocess
import sys
import os
import platform
import time
import signal

def handle_exit(signum, frame):
    print("\nStopping servers...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def start_servers():
    # Determine the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, 'frontend')
    
    # Determine OS
    is_windows = platform.system().lower() == 'windows'
    
    # Commands
    # Backend: Run from project root
    # Using sys.executable to ensure we use the active python interpreter
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]
    
    # Frontend: Run from frontend dir
    npm_cmd = "npm.cmd" if is_windows else "npm"
    frontend_cmd = [npm_cmd, "run", "dev"]

    print("🚀 Starting Trade Mart servers...")
    
    processes = []
    
    try:
        # Start Backend
        print(f"📦 Starting Backend (Uvicorn)...")
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=project_root,
            # Windows needs shell=False usually for list args, but sometimes True helps with path resolution if not full path
            # Using list args is safer and cross-platform compatible without shell=True for python executable
            shell=False
        )
        processes.append(backend_process)

        # Start Frontend
        print(f"🎨 Starting Frontend (Vite)...")
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_dir,
            shell=False 
        )
        processes.append(frontend_process)

        print("\n✅ Both servers are running!")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:5173")
        print("\nPress Ctrl+C to stop both servers.")

        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if any process has exited unexpectedly
            if backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\nStopping servers...")
    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find executable. {e}")
        if not is_windows and "npm" in str(e):
             print("Make sure 'npm' is installed and in your PATH.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        # Terminate processes
        for p in processes:
            if p.poll() is None:  # If still running
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("Goodbye!")

if __name__ == "__main__":
    start_servers()
