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