import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_app_bundle():
    """Create the .app bundle structure."""
    print("Creating application bundle...")
    
    # Define paths
    app_name = "Trace.app"
    app_path = os.path.expanduser(f"~/Desktop/{app_name}")
    contents_path = os.path.join(app_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    python_path = os.path.join(resources_path, "python")
    
    # Clean any existing build
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
    
    # Create directory structure
    os.makedirs(macos_path, mode=0o755)
    os.makedirs(resources_path, mode=0o755)
    os.makedirs(python_path, mode=0o755)
    
    # Copy application files
    print("Copying application files...")
    shutil.copytree("alert_templates", os.path.join(resources_path, "alert_templates"), dirs_exist_ok=True)
    shutil.copy("Trace_v1.py", os.path.join(resources_path, "Trace_v1.py"))
    shutil.copy("update_manager.py", os.path.join(resources_path, "update_manager.py"))
    shutil.copy("install_certificates.py", os.path.join(resources_path, "install_certificates.py"))
    shutil.copy("requirements.txt", os.path.join(resources_path, "requirements.txt"))
    
    # Create virtual environment inside the app bundle
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", python_path], check=True)
    
    # Install requirements
    pip_path = os.path.join(python_path, "bin", "pip")
    subprocess.run([pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    # Create Info.plist
    print("Creating Info.plist...")
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
    <key>CFBundleIconFile</key>
    <string>AppIcon.icns</string>
</dict>
</plist>''')
    os.chmod(plist_path, 0o644)
    
    # Create launcher script
    print("Creating launcher script...")
    launcher_path = os.path.join(macos_path, "Trace")
    with open(launcher_path, "w") as f:
        f.write('''#!/bin/bash
cd "$(dirname "$0")/../Resources"
"$(dirname "$0")/../Resources/python/bin/python3" Trace_v1.py
''')
    os.chmod(launcher_path, 0o755)
    
    # Set permissions for the entire bundle
    print("Setting permissions...")
    for root, dirs, files in os.walk(app_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            filepath = os.path.join(root, f)
            if os.access(filepath, os.X_OK) or filepath.endswith('.py') or filepath.endswith('.sh'):
                os.chmod(filepath, 0o755)
            else:
                os.chmod(filepath, 0o644)
    
    # Code sign the app bundle
    print("Code signing app bundle...")
    try:
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Code signing failed: {e}")
    
    print(f"App bundle created at: {app_path}")
    return app_path

def create_installer_package(app_path):
    """Create the installer package."""
    print("Creating installer package...")
    
    # Create temporary directory for package contents
    temp_dir = os.path.expanduser("~/Desktop/Trace_Package")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Copy app to package directory
    print("Copying app to package directory...")
    shutil.copytree(app_path, os.path.join(temp_dir, "Trace.app"))
    
    # Create postinstall script to create desktop shortcut
    postinstall_script = os.path.join(temp_dir, "postinstall")
    with open(postinstall_script, "w") as f:
        f.write('''#!/bin/bash
# Create desktop shortcut
osascript <<EOF
tell application "Finder"
    make new alias file to POSIX file "/Applications/Trace.app" at POSIX file "$HOME/Desktop"
    set name of result to "Trace"
end tell
EOF
''')
    os.chmod(postinstall_script, 0o755)
    
    # Create distribution.xml
    print("Creating distribution.xml...")
    dist_path = os.path.join(temp_dir, "distribution.xml")
    with open(dist_path, "w") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
    <title>Trace - Investigation Toolkit</title>
    <organization>com.circle.trace</organization>
    <domains enable_localSystem="true"/>
    <options customize="never" require-scripts="true"/>
    <volume-check>
        <allowed-os-versions>
            <os-version min="10.15"/>
        </allowed-os-versions>
    </volume-check>
    <choices-outline>
        <line choice="default">
            <line choice="trace"/>
        </line>
    </choices-outline>
    <choice id="default"/>
    <choice id="trace" title="Trace">
        <pkg-ref id="com.circle.trace"/>
    </choice>
    <pkg-ref id="com.circle.trace" auth="Root">Trace.pkg</pkg-ref>
</installer-gui-script>''')
    
    # Create component package
    print("Creating component package...")
    pkg_path = os.path.join(temp_dir, "Trace.pkg")
    subprocess.run([
        "pkgbuild",
        "--root", temp_dir,
        "--install-location", "/Applications",
        "--identifier", "com.circle.trace",
        "--version", "1.0.0",
        "--scripts", os.path.dirname(postinstall_script),
        pkg_path
    ], check=True)
    
    # Create final installer
    print("Creating final installer...")
    final_installer = os.path.expanduser("~/Desktop/Trace-Installer.pkg")
    subprocess.run([
        "productbuild",
        "--distribution", dist_path,
        "--package-path", temp_dir,
        "--version", "1.0.0",
        final_installer
    ], check=True)
    
    # Clean up
    print("Cleaning up...")
    shutil.rmtree(temp_dir)
    
    return final_installer

def create_macos_app():
    """Create a standalone macOS application bundle."""
    print("Creating macOS application bundle...")
    
    # Define paths
    app_name = "Trace.app"
    app_path = os.path.expanduser(f"/Applications/{app_name}")
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
    shutil.copy("Trace_v1.py", os.path.join(resources_path, "Trace_v1.py"))
    shutil.copy("update_manager.py", os.path.join(resources_path, "update_manager.py"))
    shutil.copy("install_certificates.py", os.path.join(resources_path, "install_certificates.py"))
    
    # Copy icon if it exists
    icon_path = os.path.join(resources_path, "AppIcon.icns")
    if os.path.exists("icons/AppIcon.icns"):
        shutil.copy("icons/AppIcon.icns", icon_path)
        print("Added application icon")
    
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
    <key>CFBundleIconFile</key>
    <string>AppIcon.icns</string>
</dict>
</plist>''')
    os.chmod(plist_path, 0o644)
    
    # Create virtual environment inside the app bundle
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", python_path], check=True)
    
    # Install requirements
    pip_path = os.path.join(python_path, "bin", "pip")
    subprocess.run([pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    # Create launcher script
    print("Creating launcher script...")
    launcher_path = os.path.join(macos_path, "Trace")
    with open(launcher_path, "w") as f:
        f.write('''#!/bin/bash
cd "$(dirname "$0")/../Resources"
"$(dirname "$0")/../Resources/python/bin/python3" Trace_v1.py
''')
    os.chmod(launcher_path, 0o755)
    
    # Set permissions for the entire bundle
    print("Setting permissions...")
    for root, dirs, files in os.walk(app_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            filepath = os.path.join(root, f)
            if os.access(filepath, os.X_OK) or filepath.endswith('.py') or filepath.endswith('.sh'):
                os.chmod(filepath, 0o755)
            else:
                os.chmod(filepath, 0o644)
    
    # Code sign the app bundle
    print("Code signing app bundle...")
    try:
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Code signing failed: {e}")
    
    print(f"App bundle created at: {app_path}")
    return app_path

def main():
    """Main build function."""
    if sys.platform != "darwin":
        print("Error: This build script only supports macOS")
        sys.exit(1)
    
    try:
        # Create the app bundle
        app_path = create_macos_app()
        
        # Create the installer package
        installer_path = create_installer_package(app_path)
        
        print("\nBuild complete!")
        print(f"Installer package created at: {installer_path}")
        print("\nYou can now distribute this installer package to users.")
        
    except Exception as e:
        print(f"Error during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 