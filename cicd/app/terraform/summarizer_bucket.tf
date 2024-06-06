resource "aws_s3_bucket" "summarizer" {
  bucket = "skehlet-${lower(local.app_id)}-summarizer"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "summarizer" {
  bucket = aws_s3_bucket.summarizer.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "summarizer_bucket_trigger" {
  bucket = aws_s3_bucket.summarizer.id
  queue {
    queue_arn     = aws_sqs_queue.summarizer_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "incoming/"
  }
}
