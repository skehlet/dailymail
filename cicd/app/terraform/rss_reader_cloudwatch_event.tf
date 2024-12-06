resource "aws_cloudwatch_event_rule" "rss_reader_cron" {
  name                = "${local.app_id}-before-digest"
  description         = "Fires in the afternoon (PT), a short while before the Digest lambda runs"
  schedule_expression = "cron(30 20 * * ? *)" # times are in UTC
}

resource "aws_cloudwatch_event_target" "trigger_rss_reader" {
  rule = aws_cloudwatch_event_rule.rss_reader_cron.name
  arn  = aws_lambda_function.rss_reader.arn
}
