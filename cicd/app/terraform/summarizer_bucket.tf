resource "aws_s3_bucket" "summarizer" {
  bucket = "skehlet-${local.app_id}-summarizer"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "summarizer" {
  bucket = aws_s3_bucket.summarizer.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
