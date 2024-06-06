
resource "aws_iam_role" "scraper" {
  name               = "${local.app_id}-ScraperRole"
  assume_role_policy = data.aws_iam_policy_document.scraper_assume_policy.json
}

data "aws_iam_policy_document" "scraper_assume_policy" {
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

data "aws_iam_policy_document" "scraper_policy" {
  statement {
    actions = ["s3:PutObject"]
    resources = ["arn:aws:s3:::skehlet-dailymail-summarizer/*"]
  }
}

resource "aws_iam_role_policy" "scraper_policy" {
  name   = "${local.app_id}-ScraperRolePolicy"
  role   = aws_iam_role.scraper.id
  policy = data.aws_iam_policy_document.scraper_policy.json
}

resource "aws_iam_role_policy_attachment" "scraper_attachment1" {
  role       = aws_iam_role.scraper.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "scraper_attachment2" {
  role       = aws_iam_role.scraper.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}
