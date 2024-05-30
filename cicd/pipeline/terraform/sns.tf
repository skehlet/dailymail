resource "aws_sns_topic" "pipeline_notifications" {
  name = "${local.pipeline_name}-ReviewNotifications"
}

data "aws_iam_policy_document" "review_notifications_policy" {
  statement {
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["codestar-notifications.amazonaws.com"]
    }
    resources = [aws_sns_topic.pipeline_notifications.arn]
  }
}

resource "aws_sns_topic_policy" "default" {
  arn    = aws_sns_topic.pipeline_notifications.arn
  policy = data.aws_iam_policy_document.review_notifications_policy.json
}

