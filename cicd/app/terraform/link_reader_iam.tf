
resource "aws_iam_role" "link_reader" {
  name               = "${local.app_id}-LinkReaderRole"
  assume_role_policy = data.aws_iam_policy_document.link_reader_assume_policy.json
}

data "aws_iam_policy_document" "link_reader_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
  }
}

data "aws_iam_policy_document" "link_reader_policy" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = ["arn:aws:secretsmanager:*:*:secret:DAILYMAIL_LINK_READER_CREDS-*"]
  }
  statement {
    actions = [
      "sqs:GetQueueUrl",
      "sqs:SendMessage",
    ]
    resources = ["arn:aws:sqs:*:*:DailyMail-ScraperQueue"]
  }
}

resource "aws_iam_role_policy" "link_reader_policy" {
  name   = "${local.app_id}-LinkReaderRolePolicy"
  role   = aws_iam_role.link_reader.id
  policy = data.aws_iam_policy_document.link_reader_policy.json
}

resource "aws_iam_role_policy_attachment" "link_reader_attachment1" {
  role       = aws_iam_role.link_reader.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
