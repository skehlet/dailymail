resource "aws_iam_role" "slack_chatbot_role" {
  name               = "${local.pipeline_name}-SlackChatBotRole"
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
    resources = [aws_sns_topic.pipeline_notifications.arn]
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
  name   = "${local.pipeline_name}-SlackChatBotRolePolicy"
  role   = aws_iam_role.slack_chatbot_role.id
  policy = data.aws_iam_policy_document.slack_chatbot_role_policy.json
}

resource "awscc_chatbot_slack_channel_configuration" "slack_chatbot_slack_config" {
  configuration_name = "${local.pipeline_name}-SlackChatBot"
  guardrail_policies = [
    "arn:aws:iam::aws:policy/ReadOnlyAccess",
  ]
  iam_role_arn       = aws_iam_role.slack_chatbot_role.arn
  logging_level      = "ERROR"
  slack_channel_id   = var.slack_channel_id
  slack_workspace_id = var.slack_workspace_id
  sns_topic_arns = [
    aws_sns_topic.pipeline_notifications.arn,
  ]
  user_role_required = false
}
