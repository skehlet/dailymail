resource "aws_lambda_function" "immediate" {
  function_name = "${local.app_id}-Immediate"
  package_type  = "Image"
  image_uri     = var.immediate_image_uri
  role          = aws_iam_role.immediate.arn
  timeout       = 30
  memory_size = 512
  environment {
    variables = {
      BUILD_ID = var.build_id
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.immediate_logs,
  ]
}

resource "aws_cloudwatch_log_group" "immediate_logs" {
  name              = "/aws/lambda/DailyMail-Immediate"
  retention_in_days = 7
}
