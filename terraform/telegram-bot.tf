# Yandex Cloud Function configuration
resource "yandex_function" "func" {
  name               = var.SERVERLESS_FUNCTION_NAME
  runtime            = "python312"
  entrypoint         = "main.handler"
  memory             = 128
  service_account_id = yandex_iam_service_account.sa.id
  user_hash          = archive_file.telegram_bot_code.output_sha256

  environment = {
    "TELEGRAM_BOT_TOKEN" = var.TELEGRAM_BOT_TOKEN
    "BUCKET_PHOTOS_NAME" = var.BUCKET_PHOTOS_NAME
    "BUCKET_FACES_NAME" = var.BUCKET_FACES_NAME
    "SA_ACCESS_KEY"      = yandex_iam_service_account_static_access_key.sa-static-key.access_key
    "SA_SECRET_KEY"      = yandex_iam_service_account_static_access_key.sa-static-key.secret_key
    "API_GATEWAY_URL"    = "https://${yandex_api_gateway.api_gateway.domain}/"
  }

  content {
    zip_filename = archive_file.telegram_bot_code.output_path
  }
}

resource "yandex_api_gateway" "api_gateway" {
  name        = "vvot39-apigw"
  description = "API Gateway для получения фотографий из Object Storage"

  spec = <<EOT
  openapi: 3.0.0
  info:
    title: Face Image API
    version: 1.0.0
  paths:
    /:
      get:
        summary: "Получить фото по ключу"
        parameters:
          - name: face
            in: query
            required: true
            schema:
              type: string
        responses:
          "200":
            description: "Фото"
            content:
              image/jpeg:
                schema:
                  type: string
                  format: binary
          "400":
            description: "Ошибка, если ключ не передан"
          "404":
            description: "Фото не найдено"
        x-yc-apigateway-integration:
          type: object_storage
          bucket: "${var.BUCKET_FACES_NAME}"
          object: "{face}"
          service_account_id: "${yandex_iam_service_account.sa.id}"
          headers:
              Content-Type: "{object.response.content-type}"
              Content-Disposition: "inline"
  EOT
}

# Package the Telegram bot code
resource "archive_file" "telegram_bot_code" {
  type        = "zip"
  source_dir  = "../telegram-bot"
  output_path = "../archive/telegram-bot.zip"
}

resource "yandex_function_iam_binding" "tg_bot_iam" {
  function_id = yandex_function.func.id
  role        = "functions.functionInvoker"
  members     = ["system:allUsers"]
}

resource "yandex_storage_bucket" "bucket_photos" {
  bucket        = var.BUCKET_PHOTOS_NAME
  force_destroy = true
}

variable "BUCKET_PHOTOS_NAME" {
  type        = string
  description = "Name for bucket that stores original photos"
}