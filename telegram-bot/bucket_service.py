import boto3
import requests
import logging
import json
from constants import SA_ACCESS_KEY, SA_SECRET_KEY, TELEGRAM_API_URL, TELEGRAM_FILE_URL, BUCKET_PHOTOS_NAME, BUCKET_FACES_NAME, API_GATEWAY_URL
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

def upload_to_bucket(key, image):
    try:
        s3.put_object(
            Bucket=BUCKET_PHOTOS_NAME,
            Key=f"{key}.jpeg",
            Body=image,
            ContentType="image/jpeg"
        )
    except ProcessingError as e:
        logger.error(f"Failed to upload to bucket: {e}")
        return None
    
def save_original_photo_to_bucket(file_id):
    file_path = get_file_path(file_id)

    image = get_image_from_telegram(file_path)

    upload_to_bucket(file_id, image)

def process_getface_command():
    """Обрабатывает команду /getface, отправляя фотографию через API Gateway."""
    unknown_faces = get_unknown_faces()

    if not unknown_faces:
        return None, "Нет новых фотографий"

    # Берем первое фото из списка
    face_key = unknown_faces[0]
    photo_url = f"{API_GATEWAY_URL}?key={face_key}"

    return photo_url, None

def get_unknown_faces():
    """Получает список фотографий с префиксом 'unknown-' из S3."""
    unknown_faces = []
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_FACES_NAME, Prefix="unknown-")
        if "Contents" in response:
            unknown_faces = [obj['Key'] for obj in response['Contents']]
    except Exception as e:
        logger.error(f"Ошибка при получении списка объектов из S3: {e}")
    return unknown_faces

def rename_face(name, file_id):
    try:
        old_filename = file_id

        template_file_name = old_filename.split("unknown-")[1]

        new_filename = f"{name.lower()}-{template_file_name}"
        
        s3.copy_object(
            CopySource={'Bucket': BUCKET_FACES_NAME, 'Key': old_filename},
            Bucket=BUCKET_FACES_NAME,
            Key=new_filename
        )
        
        # Удаляем исходный объект
        s3.delete_object(Bucket=BUCKET_FACES_NAME, Key=old_filename)
    except Exception as e: 
        print(str(e))
        raise e

def find_faces_by_name(name: str):
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_FACES_NAME, Prefix=f"{name.lower()}-")
        
        if "Contents" not in response:
            return []

        for obj in response["Contents"]:
            print(obj)
        # Формируем список URL фотографий
        photo_urls = [
            f"{API_GATEWAY_URL}getPhotoByName?key={obj['Key'].split("--")[1]}"
            for obj in response["Contents"]
        ]

        return photo_urls

    except Exception as e:
        logger.error(f"Ошибка при поиске фотографий для {name}: {e}")
        return []
