resource "aws_dynamodb_table" "rss_reader_processed_ids_table" {
  name         = "dailymail-rss-reader-processed-ids-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "url"
  range_key    = "id"

  attribute {
    name = "url"
    type = "S"
  }

  attribute {
    name = "id"
    type = "S"
  }
}
