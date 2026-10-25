// Per-topic memory of what Google Alert news has already been sent, see src/digest/ledger.py
resource "aws_s3_bucket" "alert_ledger" {
  bucket = "skehlet-${lower(local.app_id)}-alert-ledger"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alert_ledger" {
  bucket = aws_s3_bucket.alert_ledger.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

// Versioned so a bad ledger update can be rolled back
resource "aws_s3_bucket_versioning" "alert_ledger" {
  bucket = aws_s3_bucket.alert_ledger.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alert_ledger" {
  bucket = aws_s3_bucket.alert_ledger.id
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}
