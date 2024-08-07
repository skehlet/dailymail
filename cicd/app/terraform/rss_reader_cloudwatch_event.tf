resource "aws_cloudwatch_event_rule" "twice_daily_prior_to_digest" {
  name                = "${local.app_id}-twice-daily-prior-to-digest"
  description         = "Fires twice daily, a short while before the Digest lambda runs"
  schedule_expression = "cron(30 13,20 * * ? *)" # times are in UTC
}

resource "aws_cloudwatch_event_target" "invoke_rss_reader_twice_daily" {
  rule = aws_cloudwatch_event_rule.twice_daily_prior_to_digest.name
  arn  = aws_lambda_function.rss_reader.arn
}
