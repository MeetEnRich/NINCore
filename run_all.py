"""
NINCore - Run All Services
==========================
This script launches both the FastAPI backend and the Streamlit dashboard
concurrently in the same terminal. It handles shutting both down cleanly 
when you exit.

Usage:
    python run_all.py
"""

import subprocess
import sys
import time

def main():
    print("=" * 60)
    print("  Starting NINCore Services (API + Dashboard)")
    print("=" * 60)

    try:
        # Start the FastAPI backend
        print("-> Starting FastAPI Backend (Port 8000)...")
        api_process = subprocess.Popen(
            [sys.executable, "run_api.py"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        # Give the API a few seconds to spin up completely
        time.sleep(3)
        
        # Start the Streamlit dashboard
        print("\n-> Starting Streamlit Dashboard (Port 8501)...")
        dashboard_process = subprocess.Popen(
            [sys.executable, "run_dashboard.py"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        print("\n[OK] Both services are running!")
        print("Press Ctrl+C to stop both services cleanly.\n")

        # Wait for processes to complete (keeps the script running)
        api_process.wait()
        dashboard_process.wait()

    except KeyboardInterrupt:
        print("\n\nInterrupt received. Shutting down NINCore services...")
        try:
            api_process.terminate()
            dashboard_process.terminate()
            api_process.wait(timeout=5)
            dashboard_process.wait(timeout=5)
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            print("Shutdown complete.")

if __name__ == "__main__":
    main()
