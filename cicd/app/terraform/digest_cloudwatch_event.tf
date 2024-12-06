resource "aws_cloudwatch_event_rule" "digest_cron" {
  name                = "${local.app_id}-digest"
  description         = "Fires in the afternoon (PT)"
  schedule_expression = "cron(0 21 * * ? *)" # times are in UTC
}

resource "aws_cloudwatch_event_target" "trigger_digest" {
  rule = aws_cloudwatch_event_rule.digest_cron.name
  arn  = aws_lambda_function.digest.arn
}
