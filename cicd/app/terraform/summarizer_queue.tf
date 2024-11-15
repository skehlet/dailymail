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

resource "aws_lambda_event_source_mapping" "summarizer_queue_trigger" {
  batch_size                         = var.summarizer_trigger_batch_size
  maximum_batching_window_in_seconds = var.summarizer_trigger_maximum_batching_window_in_seconds
  event_source_arn                   = aws_sqs_queue.summarizer_queue.arn
  function_name                      = aws_lambda_function.summarizer.arn
  scaling_config {
    # Only invoke two instances (the minimum) of the summarizer at a time due to OpenAI rate limits
    # Keeping it at 2 (the minimum) also reduces the long-polling related costs
    maximum_concurrency = 2
  }
}

resource "aws_sqs_queue" "summarizer_queue_dlq" {
  name                      = "${local.app_id}-SummarizerQueue-dlq"
  message_retention_seconds = 86400 * 7
}

resource "aws_sqs_queue_redrive_allow_policy" "summarizer_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.summarizer_queue_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.summarizer_queue.arn]
  })
}

resource "aws_cloudwatch_metric_alarm" "summarizer_queue_dlq_alarm" {
  alarm_name                = "${local.app_id}-SummarizerQueue-dlq-alarm"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  threshold                 = "0"
  alarm_description         = "Trigger an alarm whenever messages are added to the DQL. Note the alarm will immediately resolve itself and trigger again for future message adds."
  insufficient_data_actions = []
  alarm_actions             = [aws_sns_topic.error_notifications.arn]

  metric_query {
    id          = "e1"
    expression  = "RATE(m2+m1)"
    label       = "Error Rate"
    return_data = "true"
  }

  metric_query {
    id = "m1"
    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = "60"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        QueueName = aws_sqs_queue.summarizer_queue_dlq.name
      }
    }
  }

  metric_query {
    id = "m2"
    metric {
      metric_name = "ApproximateNumberOfMessagesNotVisible"
      namespace   = "AWS/SQS"
      period      = "60"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        QueueName = aws_sqs_queue.summarizer_queue_dlq.name
      }
    }
  }
}
