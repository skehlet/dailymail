resource "aws_lambda_function" "email_reader" {
  function_name = "${local.app_id}-EmailReader"
  package_type  = "Image"
  image_uri     = var.email_reader_image_uri
  role          = aws_iam_role.email_reader.arn
  timeout       = 30
  memory_size   = 256
  environment {
    variables = {
      BUILD_ID = var.build_id
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.email_reader_logs,
  ]
}

resource "aws_cloudwatch_log_group" "email_reader_logs" {
  name              = "/aws/lambda/DailyMail-EmailReader"
  retention_in_days = 7
}

resource "aws_lambda_permission" "allow_sns_to_call_email_reader" {
  statement_id  = "AllowExecutionFromSns"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.email_reader.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.email_reader_topic.arn
}

resource "aws_sns_topic_subscription" "email_reader_sns_subscription" {
  topic_arn = aws_sns_topic.email_reader_topic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.email_reader.arn
}
