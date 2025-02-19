# Yandex Cloud Function configuration
resource "yandex_function" "func_face_cut" {
  name               = var.FACE_CUT_FUNCTION_NAME
  runtime            = "python312"
  entrypoint         = "main.handler"
  memory             = 128
  service_account_id = yandex_iam_service_account.sa.id
  user_hash          = archive_file.face_cut_code.output_sha256

  environment = {
    "TELEGRAM_BOT_TOKEN" = var.TELEGRAM_BOT_TOKEN
    "BUCKET_PHOTOS_NAME" = var.BUCKET_PHOTOS_NAME
    "BUCKET_FACES_NAME" = var.BUCKET_FACES_NAME
    "SA_ACCESS_KEY"      = yandex_iam_service_account_static_access_key.sa-static-key.access_key
    "SA_SECRET_KEY"      = yandex_iam_service_account_static_access_key.sa-static-key.secret_key
  }

  content {
    zip_filename = archive_file.face_cut_code.output_path
  }

  mounts {
    name = yandex_storage_bucket.bucket_faces.bucket
    mode = "rw"
    object_storage {
      bucket = yandex_storage_bucket.bucket_faces.bucket
    }
  }

  mounts {
    name = yandex_storage_bucket.bucket_photos.bucket
    mode = "ro"
    object_storage {
      bucket = yandex_storage_bucket.bucket_photos.bucket
    }
  }
}

# Package the Telegram bot code
resource "archive_file" "face_cut_code" {
  type        = "zip"
  source_dir  = "../face-cut"
  output_path = "../archive/face-cut.zip"
}

resource "yandex_function_trigger" "task_queue_trigger" {
  name = var.TASK_QUEUE_TRIGGER
  function {
    id                 = yandex_function.func_face_cut.id
    service_account_id = yandex_iam_service_account.sa.id
  }
  message_queue {
    batch_cutoff       = "10"
    batch_size         = "1"
    queue_id           = yandex_message_queue.task_queue.arn
    service_account_id = yandex_iam_service_account.sa.id
  }
}

resource "yandex_storage_bucket" "bucket_faces" {
  bucket        = var.BUCKET_FACES_NAME
  force_destroy = true
}

variable "FACE_CUT_FUNCTION_NAME" {
  type        = string
  description = "Name for serverless function that cuts faces"
}

variable "TASK_QUEUE_TRIGGER" {
  type        = string
  description = "Name for trigger that activates when task queue has tasks"
}

variable "BUCKET_FACES_NAME" {
  type        = string
  description = "Name for bucket that stores faces photos"
}