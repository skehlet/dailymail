
resource "aws_iam_role" "codepipeline_role" {
  name               = "${local.pipeline_name}-CodePipelineRole"
  assume_role_policy = data.aws_iam_policy_document.codepipeline_role_assume_policy.json
}

data "aws_iam_policy_document" "codepipeline_role_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "codepipeline.amazonaws.com",
      ]
    }
  }
}

data "aws_iam_policy_document" "codepipeline_role_policy" {
  statement {
    actions = ["codestar-connections:UseConnection"]
    resources = [
      aws_codestarconnections_connection.dailymail_github.arn
    ]
  }
  statement {
    actions = [
      "codebuild:StartBuild",
      "codebuild:BatchGetBuilds",
      "sns:Publish",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "s3:Get*",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.artifacts.arn
    ]
  }
  statement {
    actions = [
      "s3:PutObject*",
      "s3:GetObject*",
    ]
    resources = [
      "${aws_s3_bucket.artifacts.arn}/*"
    ]
  }
  statement {
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.pipeline_notifications.arn]
  }
}

resource "aws_iam_role_policy" "codepipeline_role_policy" {
  name   = "${local.pipeline_name}-CodePipelineRolePolicy"
  role   = aws_iam_role.codepipeline_role.id
  policy = data.aws_iam_policy_document.codepipeline_role_policy.json
}
