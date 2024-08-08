
resource "aws_iam_role" "rss_reader" {
  name               = "${local.app_id}-RssReaderRole"
  assume_role_policy = data.aws_iam_policy_document.rss_reader_assume_policy.json
}

data "aws_iam_policy_document" "rss_reader_assume_policy" {
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

data "aws_iam_policy_document" "rss_reader_policy" {
  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    resources = [
      "arn:aws:dynamodb:*:*:table/DailyMail-*"
    ]
  }
  statement {
    actions = [
      "sqs:GetQueueUrl",
      "sqs:SendMessage",
    ]
    resources = ["arn:aws:sqs:*:*:DailyMail-ScraperQueue"]
  }
  statement {
    actions = ["ssm:GetParameter"]
    resources = ["arn:aws:ssm:*:*:parameter/DAILY_MAIL_*"]
  }
}

resource "aws_iam_role_policy" "rss_reader_policy" {
  name   = "${local.app_id}-RssReaderRolePolicy"
  role   = aws_iam_role.rss_reader.id
  policy = data.aws_iam_policy_document.rss_reader_policy.json
}

resource "aws_iam_role_policy_attachment" "rss_reader_attachment1" {
  role       = aws_iam_role.rss_reader.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
