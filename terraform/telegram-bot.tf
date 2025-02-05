# Yandex Cloud Function configuration
resource "yandex_function" "func" {
  name               = var.SERVERLESS_FUNCTION_NAME
  runtime            = "python312"
  entrypoint         = "main.handler"
  memory             = 128
  service_account_id = yandex_iam_service_account.sa_tg_bot.id
  user_hash          = archive_file.telegram_bot_code.output_sha256

  environment = {
    "TELEGRAM_BOT_TOKEN" = var.TELEGRAM_BOT_TOKEN
  }

  content {
    zip_filename = archive_file.telegram_bot_code.output_path
  }
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