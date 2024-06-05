resource "aws_cloudwatch_event_rule" "twice_daily_prior_to_digest" {
  name                = "${local.app_id}-twice-daily-prior-to-digest"
  description         = "Fires twice daily, just prior to the Digest lambda running"
  # schedule_expression = "cron(30 12,20 * * ? *)" # times are in UTC
  schedule_expression = "cron(55 20 * * ? *)" # times are in UTC
}

resource "aws_cloudwatch_event_target" "invoke_rss_reader_twice_daily" {
  rule = aws_cloudwatch_event_rule.twice_daily_prior_to_digest.name
  arn  = aws_lambda_function.rss_reader.arn
}
