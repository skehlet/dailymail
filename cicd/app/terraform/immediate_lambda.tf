resource "aws_lambda_function" "immediate" {
  function_name = "${local.app_id}-Immediate"
  package_type  = "Image"
  image_uri     = var.immediate_image_uri
  architectures = ["arm64"]
  role          = aws_iam_role.immediate.arn
  timeout       = 30
  memory_size   = 512
  environment {
    variables = {
      PIPELINE_EXECUTION_ID = var.pipeline_execution_id
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
