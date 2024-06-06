// Read https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-queueconfig
resource "aws_sqs_queue" "summarizer_queue" {
  name                      = "${local.app_id}-SummarizerQueue"
  policy                    = data.aws_iam_policy_document.summarizer_queue_policy.json
  message_retention_seconds = 86400 * 2
  // We recommend setting your queue's visibility timeout to six times your
  // function timeout, plus the value of MaximumBatchingWindowInSeconds
  visibility_timeout_seconds = (6 * aws_lambda_function.summarizer.timeout) + var.summarizer_trigger_maximum_batching_window_in_seconds
  receive_wait_time_seconds  = 20
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.summarizer_queue_dlq.arn
    maxReceiveCount     = 5 // 5 is recommended
  })
}

data "aws_iam_policy_document" "summarizer_queue_policy" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["${data.aws_caller_identity.current.account_id}"]
    }
    actions   = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:*:*:${local.app_id}-SummarizerQueue"]
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.summarizer.arn]
    }
  }
}

resource "aws_sqs_queue" "summarizer_queue_dlq" {
  name = "${local.app_id}-SummarizerQueue-dlq"
}

resource "aws_sqs_queue_redrive_allow_policy" "summarizer_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.summarizer_queue_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.summarizer_queue.arn]
  })
}
