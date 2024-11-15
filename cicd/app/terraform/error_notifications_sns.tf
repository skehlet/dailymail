resource "aws_sns_topic" "error_notifications" {
  name = "${local.app_id}-ErrorNotifications"
}

# I think this is not necessary
# data "aws_iam_policy_document" "error_notifications_policy" {
#   statement {
#     actions = ["sns:Publish"]
#     principals {
#       type        = "Service"
#       identifiers = ["codestar-notifications.amazonaws.com"] # FIXME: cloudwatch ?
#     }
#     resources = [aws_sns_topic.error_notifications.arn]
#   }
# }

# resource "aws_sns_topic_policy" "default" {
#   arn    = aws_sns_topic.error_notifications.arn
#   policy = data.aws_iam_policy_document.error_notifications_policy.json
# }

