resource "aws_ses_receipt_rule" "email_reader_sns_rule" {
  name          = "InvokeEmailReaderFunctionLambda"
  rule_set_name = "default"
  enabled       = true
  scan_enabled  = true

  sns_action {
    topic_arn = aws_sns_topic.email_reader_topic.arn
    position  = 1
  }

  recipients = [
    "digest@ai.stevekehlet.com",
  ]
}
