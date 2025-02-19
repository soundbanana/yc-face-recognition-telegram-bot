import os
import cv2
import boto3
import logging
from json import dumps

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Переменные окружения
BUCKET_PHOTOS_NAME = os.getenv("BUCKET_PHOTOS_NAME")
QUEUE_ID = os.getenv("QUEUE_ID")
SA_ACCESS_KEY = os.getenv("SA_ACCESS_KEY")
SA_SECRET_KEY = os.getenv("SA_SECRET_KEY")

# Инициализация клиента для SQS
queue = boto3.client(
    service_name="sqs",
    endpoint_url="https://message-queue.api.cloud.yandex.net",
    region_name="ru-central1",
    aws_access_key_id=SA_ACCESS_KEY,
    aws_secret_access_key=SA_SECRET_KEY,
)

# Функция для обнаружения лиц
def detect_faces(image_path):
    # Загружаем изображение
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")

    height, width = image.shape[:2]
    logger.info(f"Размер изображения: {width}x{height}, пикселей: {width * height}")

    # Переводим изображение в черно-белое
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Загружаем классификатор для поиска лиц
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    if face_cascade.empty():
        raise ValueError("Не удалось загрузить определитель лиц.")

    # Обнаруживаем лица
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.05,
        minNeighbors=6,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Возвращаем координаты найденных лиц
    return [list(map(int, face)) for face in faces]

# Основная функция обработчика события
def handler(event, context):
    try:
        # Извлекаем object_id из сообщения
        object_id = event['messages'][0]['details']['object_id']
        image_path = f"/function/storage/{BUCKET_PHOTOS_NAME}/{object_id}"

        # Обнаруживаем лица на изображении
        faces = detect_faces(image_path)

        # Отправляем найденные лица в очередь для дальнейшей обработки
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
