resource "aws_iam_role" "codebuild_role" {
  name               = "${local.pipeline_name}-CodeBuildRole"
  assume_role_policy = data.aws_iam_policy_document.codebuild_role_assume_policy.json
}

data "aws_iam_policy_document" "codebuild_role_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "codebuild.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "codebuild_role_policy" {
  statement {
    actions = [
      "logs:DescribeLogGroups",
    ]
    resources = [
      "arn:aws:logs:*:*:log-group::log-stream:",
    ]
  }
  statement {
    actions = [
      "logs:*",
    ]
    resources = [
      "arn:aws:logs:*:*:log-group:/aws/codebuild/DailyMailPipeline-*",
    ]
  }
  statement {
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = [
      "arn:aws:s3:::skehlet-terraformstate",
      "arn:aws:s3:::skehlet-terraformstate/*",
    ]
  }
  statement {
    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]
    resources = [
      "arn:aws:dynamodb:*:*:table/terraform-state"
    ]
  }
  statement {
    actions = [
      "s3:Get*",
      "s3:ListBucket",
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketVersioning",
    ]
    resources = [
      aws_s3_bucket.artifacts.arn,
      "${aws_s3_bucket.artifacts.arn}/*",
    ]
  }
  statement {
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }
  statement {
    actions = ["ecr:*"]
    resources = [
      "arn:aws:ecr:*:*:repository/dailymail-*",
    ]
  }

  # The above permissions are the basics needed to operate the build pipeline.
  # Permissions below this line are for the app's buildspec scripts, terraform plan/apply, etc

  statement {
    actions   = ["logs:*"]
    resources = ["arn:aws:logs:*:*:log-group:/aws/lambda/DailyMail-*"]
  }
  statement {
    actions   = ["dynamodb:*"]
    resources = ["arn:aws:dynamodb:*:*:table/DailyMail-*"]
  }
  statement {
    actions   = ["iam:*"]
    resources = ["arn:aws:iam::*:role/DailyMail-*"]
  }
  statement {
    actions   = ["lambda:*"]
    resources = ["arn:aws:lambda:*:*:function:DailyMail-*"]
  }
  statement {
    actions = [
      "lambda:CreateEventSourceMapping",
      "lambda:GetEventSourceMapping",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "lambda:DeleteEventSourceMapping",
      "lambda:UpdateEventSourceMapping",
    ]
    resources = ["arn:aws:lambda:*:*:event-source-mapping:*"]
  }
  statement {
    actions   = ["sqs:*"]
    resources = ["arn:aws:sqs:*:*:DailyMail-*"]
  }
  statement {
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::skehlet-dailymail-*",
      "arn:aws:s3:::skehlet-dailymail-*/*",
    ]
  }
  statement {
    actions   = ["events:*"]
    resources = ["arn:aws:events:*:*:rule/DailyMail-*"]
  }
  statement {
    actions   = ["sns:*"]
    resources = ["arn:aws:sns:*:*:DailyMail-*"]
  }
  statement {
    actions   = ["ses:*"]
    resources = ["*"]
  }
  statement {
    actions   = ["cloudformation:*"] # Needed for ChatBot/Slack
    resources = ["*"]
  }
  statement {
    actions   = ["chatbot:*"]
    resources = ["*"]
  }
  statement {
    actions   = ["cloudwatch:*"] # Needed for alarms
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "codebuild_role_policy" {
  name   = "${local.pipeline_name}-CodeBuildRolePolicy"
  role   = aws_iam_role.codebuild_role.id
  policy = data.aws_iam_policy_document.codebuild_role_policy.json
}
