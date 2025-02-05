terraform {
  required_version = ">= 0.13"

  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
    telegram = {
      source = "yi-jiayu/telegram"
    }
  }
}

# Yandex Cloud provider configuration
provider "yandex" {
  cloud_id                 = var.CLOUD_ID
  folder_id                = var.FOLDER_ID
  service_account_key_file = var.SERVICE_ACCOUNT_KEY_FILE_PATH
}

# Telegram provider configuration
provider "telegram" {
  bot_token = var.TELEGRAM_BOT_TOKEN
}