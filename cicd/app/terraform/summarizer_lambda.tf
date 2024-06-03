resource "aws_lambda_function" "summarizer" {
  function_name = "${local.app_id}-Summarizer"
  package_type  = "Image"
  image_uri     = var.summarizer_image_uri
  role          = aws_iam_role.summarizer.arn
  timeout       = 30
  memory_size = 512
  environment {
    variables = {
      BUILD_ID = var.build_id
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.summarizer_logs,
  ]
}

resource "aws_cloudwatch_log_group" "summarizer_logs" {
  name              = "/aws/lambda/DailyMail-Summarizer"
  retention_in_days = 7
}

resource "aws_lambda_permission" "summarizer_allow_bucket_notifications" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.summarizer.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.summarizer.arn
}
