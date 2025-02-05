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