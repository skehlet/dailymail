resource "aws_cloudwatch_event_rule" "digest" {
  name                = "${local.app_id}-digest"
  description         = "Fires in the afternoon (PT)"
  schedule_expression = "cron(0 21 * * ? *)" # times are in UTC
}

resource "aws_cloudwatch_event_target" "invoke_digest_twice_daily" {
  rule = aws_cloudwatch_event_rule.digest.name
  arn  = aws_lambda_function.digest.arn
}
