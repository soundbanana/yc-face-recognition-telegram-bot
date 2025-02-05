# Variables
variable "CLOUD_ID" {
  type        = string
  description = "Yandex Cloud ID."
}

variable "FOLDER_ID" {
  type        = string
  description = "Yandex Cloud Folder ID."
}

variable "SERVICE_ACCOUNT_KEY_FILE_PATH" {
  type        = string
  description = "Path to the key for service account with admin role."
}

variable "ADMIN_SERVICE_ACCOUNT_ID" {
  type        = string
  description = "Admin Service Account ID"
}

variable "TG_BOT_SERVICE_ACCOUNT_NAME" {
  type        = string
  description = "Auxiliary Service Account Name"
}

variable "SERVERLESS_FUNCTION_NAME" {
  type        = string
  description = "Name for the serverless function in Yandex Cloud"
}

variable "TELEGRAM_BOT_TOKEN" {
  type        = string
  description = "Telegram Bot API Token."
}