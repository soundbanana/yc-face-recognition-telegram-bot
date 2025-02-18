import os
import logging
import cv2
import boto3
from json import dumps
import resource

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_PHOTOS_NAME = os.getenv("BUCKET_PHOTOS_NAME")
SA_ACCESS_KEY = os.getenv("SA_ACCESS_KEY")
SA_SECRET_KEY = os.getenv("SA_SECRET_KEY")
QUEUE_ID = os.getenv("QUEUE_ID")

queue = boto3.client(
    service_name="sqs",
    endpoint_url="https://message-queue.api.cloud.yandex.net",
    region_name="ru-central1",
    aws_access_key_id=SA_ACCESS_KEY,
    aws_secret_access_key=SA_SECRET_KEY,
)

def check_memory():
    available_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # В MB
    logger.info(f"Используемая память: {available_memory:.2f} MB")
    return available_memory

def load_and_process_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_REDUCED_GRAYSCALE_2)  # Уменьшает размер в 4 раза
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")
    
    height, width = image.shape[:2]
    logger.info(f"Размер изображения: {width}x{height}, пикселей: {width * height}")
    
    # Ограничение размера изображения
    max_size = 512  # Уменьшаем размер до 512 пикселей
    scale_factor = max_size / max(height, width)
    if scale_factor < 1:
        image = cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)))
    
    return image

def detect_faces(image):
    cascade = cv2.CascadeClassifier(f"{cv2.data.haarcascades}haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30), maxSize=(300, 300))
    return [list(map(int, face)) for face in faces]

def handler(event, context):
    try:
        check_memory()

        object_id = event['messages'][0]['details']['object_id']
        image_path = f"/function/storage/{BUCKET_PHOTOS_NAME}/{object_id}"

        image = load_and_process_image(image_path)
        faces = detect_faces(image)
        
        for face in faces:
            queue.send_message(
                QueueUrl=QUEUE_ID,
                MessageBody=dumps({"object_id": object_id, "rectangle": face})
            )

        logger.info(f"Обнаруженные лица: {faces}")
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
    finally:
        cv2.destroyAllWindows()
