from drive_upload import get_drive_service, upload_file
import os

def main():
    print("Testing upload...")
    service = get_drive_service('credentials.json', 'token.json')
    test_file_path = 'test_upload.txt'
    
    if os.path.exists(test_file_path):
        file_id = upload_file(service, test_file_path)
        print(f"Test complete! File ID created: {file_id}")
    else:
        print("Test file not found.")

if __name__ == '__main__':
    main()
