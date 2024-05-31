resource "aws_dynamodb_table" "rss_reader_feed_metadata_table" {
  name         = "${local.app_id}-RssReaderFeedMetadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "url"

  attribute {
    name = "url"
    type = "S"
  }
}
