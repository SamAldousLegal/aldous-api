from avtal.sms import extend_and_save_csv


if __name__ == "__main__":
    extend_and_save_csv()

    # sftp = SFTPClient()
    # try:
    #     sftp.connect()
    #     print("Files:", sftp.list_directory(remote_path="/appfolio"))
    #     sftp.download_file(remote_path="/appfolio/AppFolio_property_2025-03-12.csv", local_path="downloads/AppFolio_property_2025-03-12.csv")  # Download file
    #     sftp.upload_file(local_path="test.txt", remote_path="/test.txt")  # Upload file
    #     sftp.move_file(remote_path="/test.txt", new_remote_path="/renamed.txt")  # Rename file
    # finally:
    #     sftp.disconnect()