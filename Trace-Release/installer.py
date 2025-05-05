import os
import sys
import subprocess
import shutil
from pathlib import Path
from install_certificates import install_certificates

def create_shortcut():
    """Create a desktop shortcut for the application."""
    if sys.platform == 'win32':
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Trace.lnk")
        
        target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Trace.exe")
        wdir = os.path.dirname(os.path.abspath(__file__))
        icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Trace.exe")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wdir
        shortcut.IconLocation = icon
        shortcut.save()
    elif sys.platform == 'darwin':
        # Create .app bundle for macOS
        app_path = os.path.expanduser("~/Applications/Trace.app")
        if not os.path.exists(app_path):
            os.makedirs(app_path)
            os.makedirs(os.path.join(app_path, "Contents", "MacOS"))
            os.makedirs(os.path.join(app_path, "Contents", "Resources"))
            
            # Create Info.plist
            with open(os.path.join(app_path, "Contents", "Info.plist"), "w") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Trace</string>
    <key>CFBundleIdentifier</key>
    <string>com.trace.app</string>
    <key>CFBundleName</key>
    <string>Trace</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
</dict>
</plist>''')
            
            # Copy the entire application structure
            app_dir = os.path.dirname(os.path.abspath(__file__))
            shutil.copytree(os.path.join(app_dir, "alert_templates"), 
                          os.path.join(app_path, "Contents", "Resources", "alert_templates"))
            
            # Create executable script
            script_path = os.path.join(app_path, "Contents", "MacOS", "Trace")
            with open(script_path, "w") as f:
                f.write(f'''#!/bin/bash
cd "$(dirname "$0")/../Resources"
python3 Trace_v3.py
''')
            os.chmod(script_path, 0o755)

def install_ssl_certificates():
    """Install and configure SSL certificates."""
    try:
        # Create a directory for application certificates
        app_cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
        os.makedirs(app_cert_dir, exist_ok=True)
        
        # Set environment variables for SSL
        os.environ['SSL_CERT_FILE'] = os.path.join(app_cert_dir, "cacert.pem")
        os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(app_cert_dir, "cacert.pem")
        
        print("SSL certificates configured successfully")
        return True
    except Exception as e:
        print(f"Error configuring SSL certificates: {e}")
        return False

def create_macos_app():
    """Create a standalone macOS application bundle."""
    print("Creating macOS application bundle...")
    
    # Define paths
    app_name = "Trace.app"
    app_path = os.path.expanduser(f"~/Applications/{app_name}")
    contents_path = os.path.join(app_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    python_path = os.path.join(resources_path, "python")
    
    # Clean any existing installation
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
    
    # Create directory structure with proper permissions
    os.makedirs(macos_path, mode=0o755)
    os.makedirs(resources_path, mode=0o755)
    os.makedirs(python_path, mode=0o755)
    
    # Copy application files
    shutil.copytree("alert_templates", os.path.join(resources_path, "alert_templates"), dirs_exist_ok=True)
    shutil.copy("Trace_v3", os.path.join(resources_path, "Trace_v3"))
    shutil.copy("update_manager.py", os.path.join(resources_path, "update_manager.py"))
    shutil.copy("install_certificates.py", os.path.join(resources_path, "install_certificates.py"))
    
    # Set permissions for copied files
    for root, dirs, files in os.walk(resources_path):
        # 755 for directories
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        # 644 for files
        for f in files:
            os.chmod(os.path.join(root, f), 0o644)
    
    # Create Info.plist
    plist_path = os.path.join(contents_path, "Info.plist")
    with open(plist_path, "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Trace</string>
    <key>CFBundleIdentifier</key>
    <string>com.circle.trace</string>
    <key>CFBundleName</key>
    <string>Trace</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>''')
    os.chmod(plist_path, 0o644)
    
    # Install SSL certificates
    print("\nInstalling SSL certificates...")
    if not install_ssl_certificates():
        print("Warning: SSL certificate installation failed. The application will use system certificates.")
    
    # Create virtual environment with all dependencies
    subprocess.run([sys.executable, "-m", "venv", python_path])
    pip_path = os.path.join(python_path, "bin", "pip")
    
    # Upgrade pip and install setuptools first
    subprocess.run([pip_path, "install", "--upgrade", "pip"])
    subprocess.run([pip_path, "install", "--upgrade", "setuptools", "wheel"])
    
    # Install all required packages
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    
    # Install packages one by one to better handle dependencies
    for req in requirements:
        try:
            subprocess.run([pip_path, "install", req], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {req}: {e}")
            continue
    
    # Install SSL certificates
    print("\nInstalling SSL certificates...")
    python_exe = os.path.join(python_path, "bin", "python3")
    os.environ["PYTHONPATH"] = resources_path
    subprocess.run([python_exe, os.path.join(resources_path, "install_certificates.py")], check=True)
    
    # Create launcher script
    launcher_path = os.path.join(macos_path, "Trace")
    with open(launcher_path, "w") as f:
        f.write(f'''#!/bin/bash
cd "$(dirname "$0")/../Resources"
export PATH="$(dirname "$0")/../Resources/python/bin:$PATH"
export PYTHONPATH="$(dirname "$0")/../Resources:$PYTHONPATH"

# Install/update SSL certificates
"$(dirname "$0")/../Resources/python/bin/python3" install_certificates.py

# Launch the application
"$(dirname "$0")/../Resources/python/bin/python3" Trace_v3
''')
    os.chmod(launcher_path, 0o755)
    
    # Set final permissions for the entire bundle
    for root, dirs, files in os.walk(app_path):
        # 755 for directories
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        # 644 for regular files, 755 for executables
        for f in files:
            filepath = os.path.join(root, f)
            if os.access(filepath, os.X_OK):
                os.chmod(filepath, 0o755)
            else:
                os.chmod(filepath, 0o644)
    
    print(f"Application bundle created at {app_path}")
    return app_path

def main():
    """Main installation function."""
    print("Starting Trace installation...")
    
    if sys.platform != "darwin":
        print("Error: This installer only supports macOS")
        sys.exit(1)
    
    try:
        app_path = create_macos_app()
        print("\nInstallation complete!")
        print(f"Trace has been installed to {app_path}")
        print("You can now launch it from your Applications folder.")
    except Exception as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 