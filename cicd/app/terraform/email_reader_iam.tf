
resource "aws_iam_role" "email_reader" {
  name               = "${local.app_id}-EmailReaderRole"
  assume_role_policy = data.aws_iam_policy_document.email_reader_assume_policy.json
}

data "aws_iam_policy_document" "email_reader_assume_policy" {
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

data "aws_iam_policy_document" "email_reader_policy" {
  statement {
    actions   = ["ses:ListIdentities"]
    resources = ["*"]
  }
  statement {
    actions   = ["s3:PutObject"]
    resources = ["arn:aws:s3:::skehlet-dailymail-summarizer/*"]
  }
}

resource "aws_iam_role_policy" "email_reader_policy" {
  name   = "${local.app_id}-EmailReaderRolePolicy"
  role   = aws_iam_role.email_reader.id
  policy = data.aws_iam_policy_document.email_reader_policy.json
}

resource "aws_iam_role_policy_attachment" "email_reader_attachment1" {
  role       = aws_iam_role.email_reader.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
