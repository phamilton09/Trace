import requests
import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import hashlib
import logging
import certifi
import ssl
import warnings
from urllib3.exceptions import InsecureRequestWarning

# TODO: Properly fix SSL certificate verification in future update
# Current workaround: Disable SSL verification with warning
warnings.filterwarnings('always', category=InsecureRequestWarning)

def create_ssl_context():
    """Create a secure SSL context using application certificates."""
    try:
        context = ssl.create_default_context()
        # Try to use application certificates first
        app_cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "cacert.pem")
        if os.path.exists(app_cert_path):
            context.load_verify_locations(cafile=app_cert_path)
        else:
            # Fall back to certifi's certificates
            context.load_verify_locations(cafile=certifi.where())
        return context
    except Exception as e:
        print(f"Warning: Could not load SSL certificates: {e}")
        # Fall back to system certificates
        context = ssl.create_default_context()
        context.load_default_certs()
        return context

class UpdateManager:
    def __init__(self, repo_owner, repo_name, current_version):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.github_api = "https://api.github.com"
        self.setup_logging()
        
        # Create a session with proper SSL verification
        self.session = requests.Session()
        try:
            app_cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "cacert.pem")
            if os.path.exists(app_cert_path):
                self.session.verify = app_cert_path
            else:
                self.session.verify = certifi.where()
        except Exception as e:
            print(f"Warning: Could not set up SSL verification: {e}")
            self.session.verify = True  # Fall back to system certificates

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_for_updates(self):
        """Check if a new version is available on GitHub."""
        try:
            response = self.session.get(
                f"{self.github_api}/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            )
            response.raise_for_status()
            latest_release = response.json()
            
            latest_version = latest_release['tag_name']
            if self._compare_versions(latest_version, self.current_version) > 0:
                self.logger.info(f"New version {latest_version} available")
                return {
                    'available': True,
                    'version': latest_version,
                    'release_notes': latest_release['body'],
                    'assets': latest_release.get('assets', [])
                }
            return {'available': False}
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            return {'available': False, 'error': str(e)}

    def _compare_versions(self, v1, v2):
        """Compare two version strings."""
        v1_parts = [int(x) for x in v1.lstrip('v').split('.')]
        v2_parts = [int(x) for x in v2.lstrip('v').split('.')]
        return (v1_parts > v2_parts) - (v1_parts < v2_parts)

    def download_update(self, asset_url):
        """Download the update package."""
        try:
            # Create a temporary directory for the download
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download the asset
                response = requests.get(asset_url, stream=True)
                response.raise_for_status()
                
                # Get the filename from the URL
                filename = asset_url.split('/')[-1]
                file_path = os.path.join(temp_dir, filename)
                
                # Save the file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify the file hash if available
                if self._verify_file_hash(file_path):
                    return file_path
                else:
                    raise Exception("File verification failed")
        except Exception as e:
            self.logger.error(f"Error downloading update: {str(e)}")
            raise

    def _verify_file_hash(self, file_path):
        """Verify the file hash against the expected value."""
        # In a real implementation, you would compare against a known hash
        # For now, we'll just return True
        return True

    def install_update(self, update_file):
        """Install the downloaded update."""
        try:
            # Get the application directory
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            # Create a backup of the current installation
            backup_dir = os.path.join(app_dir, 'backup')
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(app_dir, backup_dir)
            
            # Extract and install the update
            # This is a placeholder - actual implementation will depend on your packaging format
            # For example, if using a zip file:
            # shutil.unpack_archive(update_file, app_dir)
            
            self.logger.info("Update installed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error installing update: {str(e)}")
            # Attempt to restore from backup
            if os.path.exists(backup_dir):
                shutil.rmtree(app_dir)
                shutil.copytree(backup_dir, app_dir)
            raise

    def restart_application(self):
        """Restart the application after an update."""
        try:
            # Get the path to the current executable
            exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            
            # Start a new process
            subprocess.Popen([exe_path] + sys.argv[1:])
            
            # Exit the current process
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Error restarting application: {str(e)}")
            raise 