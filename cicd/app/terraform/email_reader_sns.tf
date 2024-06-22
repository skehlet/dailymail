resource "aws_sns_topic" "email_reader_topic" {
  name = "${local.app_id}-EmailReaderTopic"
}

# It says this is not necessary
# If you own the Amazon SNS topic, you don't need to do anything to give Amazon SES permission to publish emails to it.
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html
# data "aws_iam_policy_document" "email_reader_topic_policy" {
#   statement {
#     actions = ["sns:Publish"]
#     principals {
#       type        = "Service"
#       identifiers = ["ses.amazonaws.com"]
#     }
#     resources = [aws_sns_topic.email_reader_topic.arn]
#   }
# }

# resource "aws_sns_topic_policy" "default" {
#   arn    = aws_sns_topic.email_reader_topic.arn
#   policy = data.aws_iam_policy_document.email_reader_topic_policy.json
# }
