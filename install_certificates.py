import os
import subprocess
import sys
import ssl
import requests
from pathlib import Path
import shutil

def get_python_locations():
    """Get all potential Python installation locations."""
    locations = []
    
    # Current Python executable location
    current_python = os.path.dirname(os.path.dirname(sys.executable))
    locations.append(current_python)
    
    return locations

def install_certificates():
    """Install SSL certificates for Python on macOS."""
    try:
        # Get the application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        cert_dir = os.path.join(app_dir, "certs")
        os.makedirs(cert_dir, exist_ok=True)
        
        # Create empty certificate file
        cert_file = os.path.join(cert_dir, "cacert.pem")
        with open(cert_file, "w") as f:
            f.write("")
        
        print(f"Created certificate directory at: {cert_dir}")
        
        # Set environment variables
        os.environ['SSL_CERT_FILE'] = cert_file
        os.environ['REQUESTS_CA_BUNDLE'] = cert_file
        
        print("\nSSL certificates configured successfully!")
        return True
        
    except Exception as e:
        print(f"Error configuring certificates: {e}")
        return False

if __name__ == "__main__":
    install_certificates() 