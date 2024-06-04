resource "aws_lambda_function" "digest" {
  function_name = "${local.app_id}-Digest"
  package_type  = "Image"
  image_uri     = var.digest_image_uri
  role          = aws_iam_role.digest.arn
  timeout       = 30
  memory_size = 512
  environment {
    variables = {
      BUILD_ID = var.build_id
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
