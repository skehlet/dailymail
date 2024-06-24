// Read https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-queueconfig
resource "aws_sqs_queue" "scraper_queue" {
  name                      = "${local.app_id}-ScraperQueue"
  message_retention_seconds = 86400 * 2
  // We recommend setting your queue's visibility timeout to six times your
  // function timeout, plus the value of MaximumBatchingWindowInSeconds
  visibility_timeout_seconds = (6 * aws_lambda_function.scraper.timeout) + var.scraper_trigger_maximum_batching_window_in_seconds
  receive_wait_time_seconds  = 20
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.scraper_queue_dlq.arn
    maxReceiveCount     = 5 // 5 is recommended
  })
}

resource "aws_sqs_queue" "scraper_queue_dlq" {
  name                      = "${local.app_id}-ScraperQueue-dlq"
  message_retention_seconds = 86400 * 7
}

resource "aws_sqs_queue_redrive_allow_policy" "scraper_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.scraper_queue_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.scraper_queue.arn]
  })
}

resource "aws_lambda_event_source_mapping" "scraper_trigger" {
  batch_size                         = var.scraper_trigger_batch_size
  maximum_batching_window_in_seconds = var.scraper_trigger_maximum_batching_window_in_seconds
  event_source_arn                   = aws_sqs_queue.scraper_queue.arn
  function_name                      = aws_lambda_function.scraper.arn
  scaling_config {
    maximum_concurrency = 2 // I had this at 10, but set to the minimum (2) to reduce long-polling costs
  }
  function_response_types = ["ReportBatchItemFailures"]
}
