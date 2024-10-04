resource "aws_codepipeline" "codepipeline" {
  name           = local.pipeline_name
  pipeline_type  = "V2"
  execution_mode = "PARALLEL"
  role_arn       = aws_iam_role.codepipeline_role.arn

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
      run_order = 1
    }
  }


  stage {
    name = "CreateImages"
    action {
      name            = "CreateRssReaderImage"
      namespace       = "CreateRssReaderImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_rssreader_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
    action {
      name            = "CreateLinkReaderImage"
      namespace       = "CreateLinkReaderImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_linkreader_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
    action {
      name            = "CreateEmailReaderImage"
      namespace       = "CreateEmailReaderImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_emailreader_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
    action {
      name            = "CreateScraperImage"
      namespace       = "CreateScraperImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_scraper_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
    action {
      name            = "CreateSummarizerImage"
      namespace       = "CreateSummarizerImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_summarizer_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
    action {
      name            = "CreateDigestImage"
      namespace       = "CreateDigestImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_digest_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
    action {
      name            = "CreateImmediateImage"
      namespace       = "CreateImmediateImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_immediate_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "AWS_ACCOUNT_ID", "value" : data.aws_caller_identity.current.account_id },
        ])
      }
      run_order = 2
    }
  }



  stage {
    name = "TerraformApply"
    action {
      name            = "TerraformApply"
      namespace       = "TerraformApply"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.dev_terraform_apply.name
        EnvironmentVariables = jsonencode([
          { "name" : "RSS_READER_IMAGE_URI", "value" : "#{CreateRssReaderImage.RSS_READER_IMAGE_URI}" },
          { "name" : "LINK_READER_IMAGE_URI", "value" : "#{CreateLinkReaderImage.LINK_READER_IMAGE_URI}" },
          { "name" : "EMAIL_READER_IMAGE_URI", "value" : "#{CreateEmailReaderImage.EMAIL_READER_IMAGE_URI}" },
          { "name" : "SCRAPER_IMAGE_URI", "value" : "#{CreateScraperImage.SCRAPER_IMAGE_URI}" },
          { "name" : "SUMMARIZER_IMAGE_URI", "value" : "#{CreateSummarizerImage.SUMMARIZER_IMAGE_URI}" },
          { "name" : "DIGEST_IMAGE_URI", "value" : "#{CreateDigestImage.DIGEST_IMAGE_URI}" },
          { "name" : "IMMEDIATE_IMAGE_URI", "value" : "#{CreateImmediateImage.IMMEDIATE_IMAGE_URI}" },
        ])
      }
      run_order = 3
    }
  }
}



resource "aws_codebuild_project" "create_rssreader_image" {
  name          = "${local.pipeline_name}-CreateRssReaderImage"
  description   = "Create RssReader Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-rssreader-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "create_linkreader_image" {
  name          = "${local.pipeline_name}-CreateLinkReaderImage"
  description   = "Create LinkReader Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-linkreader-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "create_emailreader_image" {
  name          = "${local.pipeline_name}-CreateEmailReaderImage"
  description   = "Create EmailReader Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-emailreader-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "create_scraper_image" {
  name          = "${local.pipeline_name}-CreateScraperImage"
  description   = "Create Scraper Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-scraper-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "create_summarizer_image" {
  name          = "${local.pipeline_name}-CreateSummarizerImage"
  description   = "Create Summarizer Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-summarizer-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "create_digest_image" {
  name          = "${local.pipeline_name}-CreateDigestImage"
  description   = "Create Digest Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-digest-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    privileged_mode = true # to allow running docker commands
  }
}

resource "aws_codebuild_project" "create_immediate_image" {
  name          = "${local.pipeline_name}-CreateImmediateImage"
  description   = "Create Immediate Image"
  build_timeout = 5
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-immediate-image.yaml"
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
    compute_type = "BUILD_GENERAL1_SMALL"
    type         = "LINUX_CONTAINER"
    image        = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
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
