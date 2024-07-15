resource "aws_lambda_function" "summarizer" {
  function_name = "${local.app_id}-Summarizer"
  package_type  = "Image"
  image_uri     = var.summarizer_image_uri
  role          = aws_iam_role.summarizer.arn
  timeout       = var.summarizer_trigger_batch_size * 20 // enough time to process an entire batch of items
  memory_size = 512
  environment {
    variables = {
      BUILD_ID            = var.build_id
      LLM                 = "claude-3-5-sonnet-20240620"
      CONTEXT_WINDOW_SIZE = "50000"
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
