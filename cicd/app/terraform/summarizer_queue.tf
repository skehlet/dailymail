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
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions   = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:*:*:${local.app_id}-SummarizerQueue"]
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.summarizer.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
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

resource "aws_lambda_event_source_mapping" "summarizer_queue_trigger" {
  batch_size                         = var.summarizer_trigger_batch_size
  maximum_batching_window_in_seconds = var.summarizer_trigger_maximum_batching_window_in_seconds
  event_source_arn                   = aws_sqs_queue.summarizer_queue.arn
  function_name                      = aws_lambda_function.summarizer.arn
  scaling_config {
    # only invoke two instances (the minimum) of the summarizer at a time due to OpenAI rate limits
    maximum_concurrency = 2
  }
}
