# Package the Telegram bot code
resource "archive_file" "bot_code" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "../archive/telegram.zip"
}

# Yandex Cloud Function configuration
resource "yandex_function" "func" {
  name               = var.SERVERLESS_FUNCTION_NAME
  runtime            = "python312"
  entrypoint         = "main.handler"
  memory             = 128
  service_account_id = yandex_iam_service_account.sa_tg_bot.id
  user_hash          = archive_file.bot_code.output_sha256

  environment = {
    "TELEGRAM_BOT_TOKEN" = var.TELEGRAM_BOT_TOKEN
  }

  content {
    zip_filename = archive_file.bot_code.output_path
  }
}

resource "yandex_function_iam_binding" "tg_bot_iam" {
  function_id = yandex_function.func.id
  role        = "functions.functionInvoker"
  members     = ["system:allUsers"]
}

# Service Account
resource "yandex_iam_service_account" "sa_tg_bot" {
  name = var.TG_BOT_SERVICE_ACCOUNT_NAME
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_ai_vision_iam" {
  folder_id = var.FOLDER_ID
  role      = "ai.vision.user"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_func_invoke_iam" {
  folder_id = var.FOLDER_ID
  role      = "functions.functionInvoker"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_ai_language_models_iam" {
  folder_id = var.FOLDER_ID
  role      = "ai.languageModels.user"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_storage_viewer_iam" {
  folder_id = var.FOLDER_ID
  role      = "storage.viewer"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}

# Set Telegram Bot Webhook
resource "telegram_bot_webhook" "set_webhook" {
  url = "https://api.telegram.org/bot${var.TELEGRAM_BOT_TOKEN}/setWebhook?url=https://functions.yandexcloud.net/${yandex_function.func.id}"
}

# Outputs
output "function_url" {
  description = "The public URL of the deployed Yandex Function."
  value       = "https://functions.yandexcloud.net/${yandex_function.func.id}"
}

output "webhook_url" {
  description = "The Telegram webhook URL configured for the bot."
  value       = telegram_bot_webhook.set_webhook.url
}