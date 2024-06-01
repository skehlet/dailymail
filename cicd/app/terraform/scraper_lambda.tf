resource "aws_lambda_function" "scraper" {
  function_name = "${local.app_id}-Scraper"
  package_type  = "Image"
  image_uri     = var.scraper_image_uri
  role          = aws_iam_role.scraper.arn
  timeout       = var.scraper_batch_size * 15 // enough time to process an entire batch of items
  memory_size   = 512
  environment {
    variables = {
      BUILD_ID = var.build_id
    }
  }
  depends_on = [
    aws_cloudwatch_log_group.scraper_logs,
  ]
}

resource "aws_cloudwatch_log_group" "scraper_logs" {
  name              = "/aws/lambda/DailyMail-Scraper"
  retention_in_days = 7
}
