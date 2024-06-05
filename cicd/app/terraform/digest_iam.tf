
resource "aws_iam_role" "digest" {
  name               = "${local.app_id}-DigestRole"
  assume_role_policy = data.aws_iam_policy_document.digest_assume_policy.json
}

data "aws_iam_policy_document" "digest_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "digest_policy" {
  statement {
    actions = [
      "sqs:GetQueueUrl",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:DeleteMessageBatch",
    ]
    resources = ["arn:aws:sqs:*:*:DailyMail-DigestQueue"]
  }
  statement {
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "digest_policy" {
  name   = "${local.app_id}-DigestRolePolicy"
  role   = aws_iam_role.digest.id
  policy = data.aws_iam_policy_document.digest_policy.json
}

resource "aws_iam_role_policy_attachment" "digest_attachment1" {
  role       = aws_iam_role.digest.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
