resource "aws_dynamodb_table" "rss_reader_id_table" {
  name         = "dailymail-rss-reader-id-table"
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
