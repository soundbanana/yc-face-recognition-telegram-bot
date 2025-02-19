import json
import os
import boto3
import base64
from http import HTTPStatus

# Конфигурация
BUCKET_NAME = os.getenv("BUCKET_PHOTOS_NAME")
SA_ACCESS_KEY = os.getenv("SA_ACCESS_KEY")
SA_SECRET_KEY = os.getenv("SA_SECRET_KEY")

# Настройка s3 клиента
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=SA_ACCESS_KEY,
    aws_secret_access_key=SA_SECRET_KEY,
)

def handler(event, context):
    """Cloud Function для API Gateway"""
    try:
        # Получаем параметры запроса
        query_params = event.get("queryStringParameters", {})
        face_key = query_params.get("face")
        
        if not face_key:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": json.dumps({"error": "Parameter 'face' is required"}),
            }
        
        # Загружаем файл из бакета
        response = s3.get_object(Bucket=BUCKET_NAME, Key=face_key)
        image_data = response["Body"].read()
        
        # Кодируем изображение в base64 (для ответа API Gateway)
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        return {
            "statusCode": HTTPStatus.OK,
            "headers": {"Content-Type": "image/jpeg"},
            "isBase64Encoded": True,
            "body": encoded_image,
        }
    
    except s3.exceptions.NoSuchKey:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({"error": "File not found"}),
        }
    except Exception as e:
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": json.dumps({"error": str(e)}),
        }