resource "aws_cloudwatch_event_rule" "before_digest" {
  name                = "${local.app_id}-before-digest"
  description         = "Fires in the afternoon (PT), a short while before the Digest lambda runs"
  schedule_expression = "cron(30 20 * * ? *)" # times are in UTC
}

resource "aws_cloudwatch_event_target" "invoke_rss_reader_twice_daily" {
  rule = aws_cloudwatch_event_rule.before_digest.name
  arn  = aws_lambda_function.rss_reader.arn
}
