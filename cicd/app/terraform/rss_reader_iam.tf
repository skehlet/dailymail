
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
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]
    resources = [
      "arn:aws:dynamodb:*:*:table/dailymail-rss-reader-etag-table"
    ]
  }
  // TODO: allow to add messages to the scrape queue
}

resource "aws_iam_role_policy" "rss_reader_policy" {
  name   = "${local.app_id}-RssReaderRolePolicy"
  role   = aws_iam_role.rss_reader.id
  policy = data.aws_iam_policy_document.rss_reader_policy.json
}

resource "aws_iam_role_policy_attachment" "terraform_lambda_policy" {
  role       = aws_iam_role.rss_reader.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
