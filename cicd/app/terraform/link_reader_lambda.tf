resource "aws_lambda_function" "link_reader" {
  function_name = "${local.app_id}-LinkReader"
  package_type  = "Image"
  image_uri     = var.link_reader_image_uri
  architectures = ["arm64"]
  role          = aws_iam_role.link_reader.arn
  timeout       = 30
  memory_size   = 128
  environment {
    variables = {
      PIPELINE_EXECUTION_ID = var.pipeline_execution_id
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.link_reader_logs,
  ]
}

resource "aws_cloudwatch_log_group" "link_reader_logs" {
  name              = "/aws/lambda/DailyMail-LinkReader"
  retention_in_days = 7
}

resource "aws_lambda_function_url" "link_reader" {
  function_name      = aws_lambda_function.link_reader.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET"]
    allow_headers     = ["authorization", "date", "keep-alive"]
    expose_headers    = ["keep-alive", "date"]
    max_age           = 86400
  }
}
