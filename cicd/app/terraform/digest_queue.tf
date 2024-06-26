// Read https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-queueconfig
resource "aws_sqs_queue" "digest_queue" {
  name                       = "${local.app_id}-DigestQueue"
  message_retention_seconds  = 86400 * 2
  visibility_timeout_seconds = 60
  receive_wait_time_seconds  = 20
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.digest_queue_dlq.arn
    maxReceiveCount     = 5 // 5 is recommended
  })
}

resource "aws_sqs_queue" "digest_queue_dlq" {
  name                      = "${local.app_id}-DigestQueue-dlq"
  message_retention_seconds = 86400 * 7
}

resource "aws_sqs_queue_redrive_allow_policy" "digest_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.digest_queue_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.digest_queue.arn]
  })
}
