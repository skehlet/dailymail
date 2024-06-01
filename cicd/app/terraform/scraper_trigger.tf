resource "aws_lambda_event_source_mapping" "scraper" {
  # batch_size = 10 // 10 is default for SQS
  maximum_batching_window_in_seconds = 5
  event_source_arn                   = aws_sqs_queue.scraper_queue.arn
  function_name                      = aws_lambda_function.scraper.arn
  scaling_config {
    maximum_concurrency = 10
  }
}