resource "aws_lambda_function" "scraper" {
  function_name = "${local.app_id}-Scraper"
  package_type  = "Image"
  image_uri     = var.scraper_image_uri
  role          = aws_iam_role.scraper.arn
  timeout       = aws_lambda_event_source_mapping.scraper.batch_size * 15 // enough time to process an entire batch of items
  memory_size   = 512
  depends_on = [
    aws_cloudwatch_log_group.scraper_logs,
  ]
}

resource "aws_cloudwatch_log_group" "scraper_logs" {
  name              = "/aws/lambda/DailyMail-Scraper"
  retention_in_days = 7
}
