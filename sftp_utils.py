import os
import paramiko
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a logger for the SFTP client
sftp_logger = logging.getLogger("sftp_logger")
sftp_logger.setLevel(logging.INFO)

# Create a file handler for logging to sftp.log
file_handler_sftp = logging.FileHandler("logs/sftp.log")
file_handler_sftp.setLevel(logging.INFO)

# Create a formatter and attach it to the handler
formatter_sftp = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler_sftp.setFormatter(formatter_sftp)

# Add the handler to the logger
sftp_logger.addHandler(file_handler_sftp)

class SFTPClient:
    def __init__(self):
        """Initialize SFTP connection using credentials from .env"""
        self.sftp = None
        self.transport = None
        self.sftp_host = os.getenv("SFTP_HOST")
        self.sftp_port = int(os.getenv("SFTP_PORT", 22))  # Default to 22 if not set
        self.sftp_username = os.getenv("SFTP_USERNAME")
        self.sftp_password = os.getenv("SFTP_PASSWORD")

    def connect(self):
        """Establish an SFTP connection."""
        try:
            transport = paramiko.Transport((self.sftp_host, self.sftp_port))
            transport.connect(username=self.sftp_username, password=self.sftp_password)
            self.sftp = paramiko.SFTPClient.from_transport(transport)
            self.transport = transport
            sftp_logger.info(f"Connected to SFTP server: {self.sftp_host}")
        except paramiko.SSHException as e:
            sftp_logger.error(f"SFTP Connection failed: {e}")
            raise Exception(f"SFTP Connection failed: {e}")

    def disconnect(self):
        """Close the SFTP connection."""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        sftp_logger.info("SFTP connection closed.")

    def list_directory(self, remote_path="/"):
        """List files and directories in the specified remote directory."""
        remote_path = "/aldous-sftp" + remote_path
        try:
            files = self.sftp.listdir(remote_path)
            sftp_logger.info(f"Listed directory: {remote_path}")
            return files
        except Exception as e:
            sftp_logger.error(f"Failed to list directory {remote_path}: {e}")
            return None

    def download_file(self, remote_path, local_path= "/"):
        """Download a file from the SFTP server."""
        remote_path = "/aldous-sftp" + remote_path
        try:
            self.sftp.get(remote_path, local_path)
            sftp_logger.info(f"Downloaded file: {remote_path} -> {local_path}")
        except Exception as e:
            sftp_logger.error(f"Failed to download file {remote_path}: {e}")
    
    def download_directory(self, remote_dir, local_dir):
        """Download a directory from the SFTP server to a local directory."""
        remote_dir = "/aldous-sftp" + remote_dir  # Ensure you're using the correct base path
        local_dir = os.path.join(local_dir, os.path.basename(remote_dir))  # Ensure local directory exists

        # Create the local directory if it doesn't exist
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        try:
            # List the files and directories in the remote directory
            remote_files = self.sftp.listdir_attr(remote_dir)

            for file_attr in remote_files:
                remote_file_path = remote_dir + "/" + file_attr.filename
                local_file_path = os.path.join(local_dir, file_attr.filename)

                if file_attr.st_mode & 0o40000:  # Check if it's a directory
                    # If it's a directory, recursively download it
                    self.download_directory(remote_file_path, local_file_path)
                else:
                    # If it's a file, download it
                    self.sftp.get(remote_file_path, local_file_path)
                    sftp_logger.info(f"Downloaded file: {remote_file_path} -> {local_file_path}")
        except Exception as e:
            sftp_logger.error(f"Failed to download directory {remote_dir}: {e}")

    def upload_file(self, local_path, remote_path="/"):
        """Upload a file to the SFTP server."""
        remote_path = "/aldous-sftp" + remote_path
        try:
            self.sftp.put(local_path, remote_path)
            sftp_logger.info(f"Uploaded file: {local_path} -> {remote_path}")
        except Exception as e:
            sftp_logger.error(f"Failed to upload file {local_path}: {e}")

    def move_file(self, remote_path, new_remote_path):
        """Move a file on the SFTP server."""
        remote_path = "/aldous-sftp" + remote_path
        new_remote_path = "/aldous-sftp" + new_remote_path
        try:
            self.sftp.rename(remote_path, new_remote_path)
            sftp_logger.info(f"Renamed file: {remote_path} -> {new_remote_path}")
        except Exception as e:
            sftp_logger.error(f"Failed to rename file {remote_path}: {e}")
