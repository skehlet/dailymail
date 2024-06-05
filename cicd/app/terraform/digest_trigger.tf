resource "aws_cloudwatch_event_rule" "twice_daily" {
  name                = "${local.app_id}-twice-daily"
  description         = "Fires twice daily"
  schedule_expression = "cron(0 6,14 * * ? *)"
}

resource "aws_cloudwatch_event_target" "invoke_digest_twice_daily" {
  rule = aws_cloudwatch_event_rule.twice_daily.name
  arn  = aws_lambda_function.digest.arn
}
