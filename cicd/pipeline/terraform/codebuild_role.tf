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

  # Allow developers to assume this role on their systems
  # TODO
}

data "aws_iam_policy_document" "codebuild_role_policy" {
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
      "dynamodb:DeleteItem"
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
      "arn:aws:ecr:*:*:repository/codebuild-terraform-image",
      "arn:aws:ecr:*:*:repository/dailymail-*",
    ]
  }

  # The above permissions are the basics needed to operate the build pipeline.
  # Permissions below this line are for the app's CodeBuild scripts, terraform plan/apply, etc
}

resource "aws_iam_role_policy" "codebuild_role_policy" {
  name   = "${local.pipeline_name}-CodeBuildRolePolicy"
  role   = aws_iam_role.codebuild_role.id
  policy = data.aws_iam_policy_document.codebuild_role_policy.json
}
