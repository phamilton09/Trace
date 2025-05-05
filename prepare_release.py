import os
import shutil
from datetime import datetime

def prepare_release():
    # Create release directory
    release_dir = "Trace-Release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Files to copy
    files_to_copy = [
        "Trace_v1.py",
        "update_manager.py",
        "install_certificates.py",
        "requirements.txt",
        "README.md",
        "build_installer.py",
        "installer.py",
        "RELEASE_NOTES.md",
        "LICENSE"
    ]
    
    # Directories to copy
    dirs_to_copy = [
        "alert_templates",
        "icons"
    ]
    
    # Copy files
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(release_dir, file))
    
    # Copy directories
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(release_dir, dir_name))
    
    # Create .gitignore
    with open(os.path.join(release_dir, ".gitignore"), "w") as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Project specific
certs/
*.pkg
Trace_Package/
""")
    
    # Create version file
    version = "1.0.0"
    with open(os.path.join(release_dir, "VERSION"), "w") as f:
        f.write(f"{version}\n")
    
    # Create zip file
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"Trace-{version}-{timestamp}.zip"
    shutil.make_archive(f"Trace-{version}-{timestamp}", 'zip', release_dir)
    
    print(f"Release prepared successfully!")
    print(f"Release directory: {release_dir}")
    print(f"Release archive: {zip_name}")

if __name__ == "__main__":
    prepare_release() 