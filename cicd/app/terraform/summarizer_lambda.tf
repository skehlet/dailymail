resource "aws_lambda_function" "summarizer" {
  function_name = "${local.app_id}-Summarizer"
  package_type  = "Image"
  image_uri     = var.summarizer_image_uri
  architectures = ["arm64"]
  role          = aws_iam_role.summarizer.arn
  timeout       = var.summarizer_trigger_batch_size * 20 // enough time to process an entire batch of items
  memory_size   = 512
  environment {
    variables = {
      PIPELINE_EXECUTION_ID = var.pipeline_execution_id
      LLM_PROVIDER          = "gemini"
      LLM                   = "gemini-2.5-flash-lite"
      CONTEXT_WINDOW_SIZE   = "50000"
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
