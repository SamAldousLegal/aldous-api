import logging
from sftp_utils import SFTPClient

# Create a logger specific to this script
tcn_logger = logging.getLogger('call_recordings_download')
tcn_logger.setLevel(logging.INFO)  # Set log level to INFO

# Create a file handler to write logs to a file
file_handler = logging.FileHandler('tcn/call_recordings_download.log')
file_handler.setLevel(logging.INFO)

# Create a formatter to specify log message format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
tcn_logger.addHandler(file_handler)

# Create a stream handler to also log to console (optional)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
tcn_logger.addHandler(console_handler)

if __name__ == "__main__":
    sftp = SFTPClient()
    
    try:
        tcn_logger.info("Starting SFTP connection...")
        sftp.connect()
        tcn_logger.info("Downloading directory from SFTP server...")
        sftp.download_directory(remote_dir="/tcn/call_recordings", local_dir="downloads/tcn")
        tcn_logger.info("Download completed successfully.")
        
    except Exception as e:
        tcn_logger.error(f"An error occurred: {e}")
    
    finally:
        tcn_logger.info("Disconnecting from SFTP server...")
        sftp.disconnect()
        tcn_logger.info("Disconnected from SFTP server.")
