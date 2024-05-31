resource "aws_sqs_queue" "scrape_queue" {
  name                       = "${local.app_id}-ScrapeQueue"
  message_retention_seconds  = 86400 * 2
  visibility_timeout_seconds = 60 * 5
  receive_wait_time_seconds  = 20
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.scrape_queue_dlq.arn
    maxReceiveCount     = 4
  })
}

resource "aws_sqs_queue" "scrape_queue_dlq" {
  name = "${local.app_id}-ScrapeQueue-dlq"
}

resource "aws_sqs_queue_redrive_allow_policy" "terraform_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.scrape_queue_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.scrape_queue.arn]
  })
}
