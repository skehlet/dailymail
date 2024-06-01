resource "aws_lambda_event_source_mapping" "scraper_trigger" {
  batch_size                         = var.scraper_trigger_batch_size
  maximum_batching_window_in_seconds = var.scraper_trigger_maximum_batching_window_in_seconds
  event_source_arn                   = aws_sqs_queue.scraper_queue.arn
  function_name                      = aws_lambda_function.scraper.arn
  scaling_config {
    maximum_concurrency = 10
  }
}
