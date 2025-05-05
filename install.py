#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import venv

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def create_venv():
    """Create a virtual environment."""
    print("Creating virtual environment...")
    try:
        venv.create("venv", with_pip=True)
    except Exception as e:
        print(f"Error: Failed to create virtual environment: {e}")
        sys.exit(1)

def install_dependencies():
    """Install required Python packages in the virtual environment."""
    print("Installing dependencies...")
    try:
        # Use the pip from the virtual environment
        if platform.system() == "Windows":
            pip_path = os.path.join("venv", "Scripts", "pip")
        else:
            pip_path = os.path.join("venv", "bin", "pip")
        
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies: {e}")
        sys.exit(1)

def check_chrome():
    """Check if Chrome is installed."""
    system = platform.system()
    if system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Windows":
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    else:  # Linux
        chrome_path = "/usr/bin/google-chrome"

    if not os.path.exists(chrome_path):
        print("Warning: Google Chrome not found. Screenshot functionality will not work.")
        print("Please install Chrome from: https://www.google.com/chrome/")

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    directories = [
        "alert_templates",
        "certs"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main installation function."""
    print("Starting Trace installation...")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_venv()
    
    # Install dependencies
    install_dependencies()
    
    # Check for Chrome
    check_chrome()
    
    # Create directories
    create_directories()
    
    print("\nInstallation complete!")
    print("\nTo run Trace:")
    print("1. Open a terminal/command prompt")
    print("2. Navigate to the Trace directory")
    print("3. Run the appropriate script:")
    print("   - Windows: run_trace.bat")
    print("   - macOS/Linux: ./run_trace.sh")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 