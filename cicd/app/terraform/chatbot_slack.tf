resource "aws_iam_role" "slack_chatbot_role" {
  name               = "${local.app_id}-SlackChatBotRole"
  assume_role_policy = data.aws_iam_policy_document.slack_chatbot_assume_role_policy.json
}

data "aws_iam_policy_document" "slack_chatbot_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["chatbot.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "slack_chatbot_role_policy" {
  statement {
    actions   = ["sns:Subscribe"]
    resources = [aws_sns_topic.error_notifications.arn]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "slack_chatbot_role_policy" {
  name   = "${local.app_id}-SlackChatBotRolePolicy"
  role   = aws_iam_role.slack_chatbot_role.id
  policy = data.aws_iam_policy_document.slack_chatbot_role_policy.json
}

resource "awscc_chatbot_slack_channel_configuration" "slack_chatbot_slack_config" {
  configuration_name = "${local.app_id}-SlackChatBot"
  guardrail_policies = [
    "arn:aws:iam::aws:policy/ReadOnlyAccess",
  ]
  iam_role_arn       = aws_iam_role.slack_chatbot_role.arn
  logging_level      = "ERROR"
  slack_channel_id   = local.slack_channel_id
  slack_workspace_id = local.slack_workspace_id
  sns_topic_arns = [
    aws_sns_topic.error_notifications.arn,
  ]
  user_role_required = false
}
