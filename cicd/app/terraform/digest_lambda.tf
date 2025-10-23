resource "aws_lambda_function" "digest" {
  function_name = "${local.app_id}-Digest"
  package_type  = "Image"
  image_uri     = var.digest_image_uri
  architectures = ["arm64"]
  role          = aws_iam_role.digest.arn
  timeout       = 180
  memory_size   = 512
  environment {
    variables = {
      PIPELINE_EXECUTION_ID = var.pipeline_execution_id
      LLM_PROVIDER          = "gemini"
      LLM                   = "gemini-2.5-flash"
      CONTEXT_WINDOW_SIZE   = "50000"
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.digest_logs,
  ]
}

resource "aws_cloudwatch_log_group" "digest_logs" {
  name              = "/aws/lambda/DailyMail-Digest"
  retention_in_days = 7
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_digest" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.digest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.digest_cron.arn
}
