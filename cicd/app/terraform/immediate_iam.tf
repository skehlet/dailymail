
resource "aws_iam_role" "immediate" {
  name               = "${local.app_id}-ImmediateRole"
  assume_role_policy = data.aws_iam_policy_document.immediate_assume_policy.json
}

data "aws_iam_policy_document" "immediate_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "immediate_policy" {
  statement {
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "immediate_policy" {
  name   = "${local.app_id}-ImmediateRolePolicy"
  role   = aws_iam_role.immediate.id
  policy = data.aws_iam_policy_document.immediate_policy.json
}

resource "aws_iam_role_policy_attachment" "immediate_attachment1" {
  role       = aws_iam_role.immediate.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "immediate_attachment2" {
  role       = aws_iam_role.immediate.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}
