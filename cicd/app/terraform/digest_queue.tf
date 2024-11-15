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

resource "aws_cloudwatch_metric_alarm" "digest_queue_dlq_alarm" {
  alarm_name                = "${local.app_id}-DigestQueue-dlq-alarm"
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
        QueueName = aws_sqs_queue.digest_queue_dlq.name
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
        QueueName = aws_sqs_queue.digest_queue_dlq.name
      }
    }
  }
}
