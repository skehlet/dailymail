
resource "aws_iam_role" "summarizer" {
  name               = "${local.app_id}-SummarizerRole"
  assume_role_policy = data.aws_iam_policy_document.summarizer_assume_policy.json
}

data "aws_iam_policy_document" "summarizer_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "summarizer_policy" {
  statement {
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::skehlet-dailymail-summarizer",
      "arn:aws:s3:::skehlet-dailymail-summarizer/*",
    ]
  }
  statement {
    actions = ["secretsmanager:GetSecretValue"]
    resources = ["arn:aws:secretsmanager:*:*:secret:OPENAI_API_KEY-*"]
  }
  statement {
    actions = [
      "sqs:GetQueueUrl",
      "sqs:SendMessage",
    ]
    resources = ["arn:aws:sqs:*:*:DailyMail-DigestQueue"]
  }
}

resource "aws_iam_role_policy" "summarizer_policy" {
  name   = "${local.app_id}-SummarizerRolePolicy"
  role   = aws_iam_role.summarizer.id
  policy = data.aws_iam_policy_document.summarizer_policy.json
}

resource "aws_iam_role_policy_attachment" "summarizer_attachment1" {
  role       = aws_iam_role.summarizer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "summarizer_attachment2" {
  role       = aws_iam_role.summarizer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}
