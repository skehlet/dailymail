// Read https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-queueconfig
resource "aws_sqs_queue" "scrape_queue" {
  name                       = "${local.app_id}-ScraperQueue"
  message_retention_seconds  = 86400 * 2
  // We recommend setting your queue's visibility timeout to six times your
  // function timeout, plus the value of MaximumBatchingWindowInSeconds
  visibility_timeout_seconds = (6 * aws_lambda_function.scraper.timeout) + aws_lambda_event_source_mapping.scraper.maximum_batching_window_in_seconds
  receive_wait_time_seconds  = 20
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.scraper_queue_dlq.arn
    maxReceiveCount     = 5 // 5 is recommended
  })
}

resource "aws_sqs_queue" "scraper_queue_dlq" {
  name = "${local.app_id}-ScraperQueue-dlq"
}

resource "aws_sqs_queue_redrive_allow_policy" "terraform_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.scraper_queue_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.scraper_queue.arn]
  })
}
