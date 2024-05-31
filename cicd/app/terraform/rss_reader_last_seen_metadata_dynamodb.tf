resource "aws_dynamodb_table" "rss_reader_feed_metadata_table" {
  name         = "dailymail-rss-reader-feed_metadata-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "url"

  attribute {
    name = "url"
    type = "S"
  }
}
