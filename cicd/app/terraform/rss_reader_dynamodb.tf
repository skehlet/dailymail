resource "aws_dynamodb_table" "pfs_etag_table" {
  name         = "dailymail-rss-reader-etag-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "url"
  range_key    = "etag"

  attribute {
    name = "url"
    type = "S"
  }

  attribute {
    name = "etag"
    type = "S"
  }
}
