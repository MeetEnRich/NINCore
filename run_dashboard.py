"""
NINCore — Dashboard Launcher
==============================
Single command to start the Streamlit dashboard.

Usage:
    python run_dashboard.py

Dashboard will open at:
    http://localhost:8501
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "dashboard" / "app.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8501",
        "--server.headless", "false",
        "--theme.base", "dark",
        "--theme.primaryColor", "#4fc3f7",
        "--theme.backgroundColor", "#0f1923",
        "--theme.secondaryBackgroundColor", "#1a2332",
        "--theme.textColor", "#e0e0e0",
    ])