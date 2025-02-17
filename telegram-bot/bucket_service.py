import boto3
import requests
import logging
import json
from constants import SA_ACCESS_KEY, SA_SECRET_KEY, TELEGRAM_API_URL, TELEGRAM_FILE_URL
from helpers import ProcessingError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id = SA_ACCESS_KEY, 
    aws_secret_access_key = SA_SECRET_KEY,
)

def get_file_path(file_id: str):
    """Retrieves the file path of a Telegram file using its file_id."""
    url = f"{TELEGRAM_API_URL}/getFile"
    try:
        response = requests.get(url, params={"file_id": file_id})
        response.raise_for_status()
        return response.json().get("result", {}).get("file_path")
    except requests.RequestException as e:
        logger.error(f"Failed to get file path: {e}", {"file_id": file_id})
        return None
    
def get_image_from_telegram(file_path: str):
    """Downloads the image content from Telegram servers."""
    url = f"{TELEGRAM_FILE_URL}/{file_path}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.error(f"Failed to download image: {e}", {"file_path": file_path})
        return None

def upload_to_bucket(bucket_name, key, image):
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=f"{key}.jpeg",
            Body=image,
            ContentType="image/jpeg"
        )
    except ProcessingError as e:
        logger.error(f"Failed to upload to bucket: {e}")
        return None
    
def save_original_photo_to_bucket(bucket_name, file_id):
        file_path = get_file_path(file_id)

        image = get_image_from_telegram(file_path)

        upload_to_bucket(bucket_name, file_id, image)