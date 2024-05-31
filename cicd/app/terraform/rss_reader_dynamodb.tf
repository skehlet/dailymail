resource "aws_dynamodb_table" "rss_reader_etag_table" {
  name         = "dailymail-rss-reader-etag-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "url"

  attribute {
    name = "url"
    type = "S"
  }

  attribute {
    name = "etag"
    type = "S"
  }
}
