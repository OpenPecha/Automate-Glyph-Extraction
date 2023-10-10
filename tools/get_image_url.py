from googleapiclient.discovery import build

API_KEY = "AIzaSyB4yvItVx9a0A_iJjEsn5uHb7zZzn4Tty0" # Replace with your actual API key
FOLDER_ID = "1UUmwLYnMKcYr0c5gGyOR5ezpoMeGv9Pb" # Replace with the folder ID you want to retrieve images from

def get_image_urls_in_folder(folder_id, api_key):
    service = build('drive', 'v3', developerKey=api_key)

    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    print("Query:", query)  # Debug print
    results = service.files().list(q=query, fields="files(webContentLink)").execute()
    print("Results:", results)  # Debug print
    image_urls = [file['webContentLink'] for file in results.get('files', [])]

    return image_urls

if __name__ == "__main__":
    image_urls = get_image_urls_in_folder(FOLDER_ID, API_KEY)
    for url in image_urls:
        print(url)
