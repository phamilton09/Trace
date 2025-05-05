#!/usr/bin/env python3
import os
import shutil
import subprocess
from datetime import datetime

def create_distribution():
    """Create a distribution package for Trace."""
    # Create dist directory
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Create Trace.app bundle
    app_dir = os.path.join(dist_dir, "Trace.app")
    os.makedirs(app_dir)
    
    # Copy required files
    files_to_copy = [
        "Trace_v3",
        "installer.py",
        "requirements.txt",
        "update_manager.py",
        "README.md"
    ]
    
    for file in files_to_copy:
        shutil.copy(file, dist_dir)
    
    # Copy alert_templates directory
    shutil.copytree("alert_templates", os.path.join(dist_dir, "alert_templates"))
    
    # Create version file
    version = "1.0.0"
    with open(os.path.join(dist_dir, "version.txt"), "w") as f:
        f.write(version)
    
    # Create the zip file
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"Trace-{version}-{timestamp}.zip"
    shutil.make_archive(os.path.join(".", zip_name.replace(".zip", "")), "zip", dist_dir)
    
    print(f"\nDistribution package created: {zip_name}")
    print("Contents:")
    print("- Trace_v3 (main application)")
    print("- installer.py (installation script)")
    print("- requirements.txt (dependencies)")
    print("- update_manager.py (update handler)")
    print("- alert_templates/ (template files)")
    print("- README.md (documentation)")
    print("- version.txt (version information)")
    
    print("\nInstructions for users:")
    print("1. Download and unzip the package")
    print("2. Double-click installer.py")
    print("3. The application will be installed to the Applications folder")

if __name__ == "__main__":
    create_distribution() 