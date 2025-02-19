import os
import boto3
import logging
import json
import uuid
from io import BytesIO
from PIL import Image, ImageDraw

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Переменные окружения
BUCKET_PHOTOS_NAME = os.getenv("BUCKET_PHOTOS_NAME")
BUCKET_FACES_NAME = os.getenv("BUCKET_FACES_NAME")
SA_ACCESS_KEY = os.getenv("SA_ACCESS_KEY")
SA_SECRET_KEY = os.getenv("SA_SECRET_KEY")

# Инициализация клиента для S3
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=SA_ACCESS_KEY,
    aws_secret_access_key=SA_SECRET_KEY
)

# Функция для рисования прямоугольника вокруг лица
def draw_white_rectangle(image_path, coordinates, filename):
    try:
        # Открываем изображение
        with Image.open(image_path) as img:
            x, y, w, h = map(int, coordinates)
            logger.info(f"Координаты для прямоугольника: x={x}, y={y}, w={w}, h={h}")
            
            # Создаем объект для рисования
            draw = ImageDraw.Draw(img)

            # Рисуем белый прямоугольник вокруг лица
            draw.rectangle((x, y, x + w, y + h), outline="white", width=5)

            # Сохраняем изображение в буфер
            format = img.format if img.format else 'JPEG'
            buffer = BytesIO()
            img.save(buffer, format=format)
            buffer.seek(0)

            # Загружаем измененное изображение в S3
            s3.put_object(
                Bucket=BUCKET_FACES_NAME,
                Key=filename,
                Body=buffer.getvalue(),
                ContentType="image/jpeg"
            )

            logger.info(f"Изображение с прямоугольниками загружено в S3: {filename}")
            return True

    except Exception as e:
        logger.error(f"Ошибка рисования прямоугольника: {str(e)}")
        raise e

# Основная функция обработчика события
def handler(event, context):
    try:
        print(event)
        # Извлекаем данные из события
        message = json.loads(event['messages'][0]['details']['message']['body'])
        object_id = message['object_id']
        coordinates = message['rectangle']

        # Формируем путь к изображению
        source_path = f"/function/storage/{BUCKET_PHOTOS_NAME}/{object_id}"
        output_object_id = f"unknown-{str(uuid.uuid4())}-{object_id}"
            
        # Рисуем прямоугольник и сохраняем изображение
        success = draw_white_rectangle(source_path, coordinates, output_object_id)
        
        if success:
            return {
                'statusCode': 200,
                'body': '{"status": "success"}'
            }
        
        raise RuntimeError("Ошибка при обработке изображения")

    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}")
        return {
            'statusCode': 500,
            'body': '{"status": "error"}'
        }
