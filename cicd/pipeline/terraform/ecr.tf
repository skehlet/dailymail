resource "aws_ecr_repository" "image_repo" {
  for_each = toset(["dailymail-rss-reader"])
  name     = each.key
}

resource "aws_ecr_lifecycle_policy" "lifecycle_policy" {
  for_each   = toset(["dailymail-rss-reader"])
  repository = aws_ecr_repository.image_repo[each.key].name
  policy = jsonencode(
    {
      "rules" : [
        {
          "rulePriority" : 1,
          "description" : "Only keep 5 images",
          "selection" : {
            "tagStatus" : "any",
            "countType" : "imageCountMoreThan",
            "countNumber" : 5
          },
          "action" : {
            "type" : "expire"
          }
        }
      ]
  })
}

data "aws_iam_policy_document" "policy" {
  for_each = toset(["dailymail-rss-reader"])
  statement {
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
    actions = [
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = [aws_codebuild_project.create_images.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }

  statement {
    principals {
      type = "AWS"
      identifiers = [
        data.aws_caller_identity.current.account_id,
      ]
    }
    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:DescribeRepositories",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
    ]
  }
}

resource "aws_ecr_repository_policy" "policy" {
  for_each   = toset(["dailymail-rss-reader"])
  repository = aws_ecr_repository.image_repo[each.key].name
  policy     = data.aws_iam_policy_document.policy[each.key].json
}
