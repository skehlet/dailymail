resource "aws_lambda_function" "rss_reader" {
  function_name = "${local.app_id}-RssReader"
  package_type  = "Image"
  image_uri     = var.rss_reader_image_uri
  architectures = ["arm64"]
  role          = aws_iam_role.rss_reader.arn
  timeout       = 180
  memory_size   = 512
  environment {
    variables = {
      PIPELINE_EXECUTION_ID = var.pipeline_execution_id
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.rss_reader_logs,
  ]
}

resource "aws_cloudwatch_log_group" "rss_reader_logs" {
  name              = "/aws/lambda/DailyMail-RssReader"
  retention_in_days = 7
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_rss_reader" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rss_reader.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.rss_reader_cron.arn
}
