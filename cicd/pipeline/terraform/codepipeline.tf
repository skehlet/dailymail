resource "aws_codepipeline" "codepipeline" {
  name     = local.pipeline_name
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      provider         = "CodeStarSourceConnection"
      owner            = "AWS"
      version          = "1"
      namespace        = "Source"
      output_artifacts = ["SourceArtifact"]
      configuration = {
        ConnectionArn    = aws_codestarconnections_connection.dailymail_github.arn
        FullRepositoryId = "skehlet/dailymail"
        BranchName       = "main"
      }
    }
  }

  stage {
    name = "CreateImages"

    action {
      name            = "CreateImages"
      namespace       = "CreateImages"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_images.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
    }
  }

  stage {
    name = "TerraformApply"

    action {
      name      = "TerraformApply"
      namespace = "TerraformApply"
      input_artifacts = ["SourceArtifact"]
      category = "Build"
      provider = "CodeBuild"
      owner    = "AWS"
      version  = "1"
      configuration = {
        ProjectName   = aws_codebuild_project.dev_terraform_apply.name
        EnvironmentVariables = jsonencode([
          { "name" : "RSS_READER_IMAGE_URI", "value" : "#{CreateImages.RSS_READER_IMAGE_URI}" },
          { "name" : "LINK_READER_IMAGE_URI", "value" : "#{CreateImages.LINK_READER_IMAGE_URI}" },
          { "name" : "EMAIL_READER_IMAGE_URI", "value" : "#{CreateImages.EMAIL_READER_IMAGE_URI}" },
          { "name" : "SCRAPER_IMAGE_URI", "value" : "#{CreateImages.SCRAPER_IMAGE_URI}" },
          { "name" : "SUMMARIZER_IMAGE_URI", "value" : "#{CreateImages.SUMMARIZER_IMAGE_URI}" },
          { "name" : "DIGEST_IMAGE_URI", "value" : "#{CreateImages.DIGEST_IMAGE_URI}" },
          { "name" : "IMMEDIATE_IMAGE_URI", "value" : "#{CreateImages.IMMEDIATE_IMAGE_URI}" },
          { "name" : "BUILD_ID", value : "#{CreateImages.BUILD_ID}" },
        ])
      }
    }
  }
}

resource "aws_codebuild_project" "create_images" {
  name          = "${local.pipeline_name}-CreateImages"
  description   = "Create Images"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-images.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "dev_terraform_apply" {
  name          = "${local.pipeline_name}-TerraformApply"
  description   = "Dev Terraform Apply"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-terraform-apply.yaml"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    type                        = "LINUX_CONTAINER"
    image                       = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/codebuild-terraform-image:${var.codebuild_terraform_image_tag}"
    image_pull_credentials_type = "SERVICE_ROLE"
  }
}

resource "aws_codestarnotifications_notification_rule" "interesting_events" {
  name     = "${local.pipeline_name}-example-code-repo-commits"
  resource = aws_codepipeline.codepipeline.arn
  event_type_ids = [
    # "codepipeline-pipeline-action-execution-canceled",
    # "codepipeline-pipeline-action-execution-failed",
    # "codepipeline-pipeline-action-execution-started",
    # "codepipeline-pipeline-action-execution-succeeded",
    # "codepipeline-pipeline-manual-approval-failed",
    "codepipeline-pipeline-manual-approval-needed",
    # "codepipeline-pipeline-manual-approval-succeeded",
    "codepipeline-pipeline-pipeline-execution-canceled",
    "codepipeline-pipeline-pipeline-execution-failed",
    "codepipeline-pipeline-pipeline-execution-resumed",
    "codepipeline-pipeline-pipeline-execution-started",
    "codepipeline-pipeline-pipeline-execution-succeeded",
    "codepipeline-pipeline-pipeline-execution-superseded",
    # "codepipeline-pipeline-stage-execution-canceled",
    # "codepipeline-pipeline-stage-execution-failed",
    # "codepipeline-pipeline-stage-execution-resumed",
    # "codepipeline-pipeline-stage-execution-started",
    # "codepipeline-pipeline-stage-execution-succeeded",
  ]
  detail_type = "FULL"
  target {
    address = aws_sns_topic.pipeline_notifications.arn
  }
}
