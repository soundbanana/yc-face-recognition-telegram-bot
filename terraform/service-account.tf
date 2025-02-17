# Service Account
resource "yandex_iam_service_account" "sa" {
  name = var.TG_BOT_SERVICE_ACCOUNT_NAME
}

// Static access key
resource "yandex_iam_service_account_static_access_key" "sa-static-key" {
  service_account_id = yandex_iam_service_account.sa.id
  description        = "Static access key for object storage"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_func_invoke_iam" {
  folder_id = var.FOLDER_ID
  role      = "functions.functionInvoker"
  member    = "serviceAccount:${yandex_iam_service_account.sa.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_storage_viewer_iam" {
  folder_id = var.FOLDER_ID
  role      = "storage.admin"
  member    = "serviceAccount:${yandex_iam_service_account.sa.id}"
}