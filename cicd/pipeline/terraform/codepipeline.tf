resource "aws_codepipeline" "codepipeline" {
  name          = local.pipeline_name
  pipeline_type = "V2"
  role_arn      = aws_iam_role.codepipeline_role.arn

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
        ConnectionArn    = aws_codeconnections_connection.dailymail_github.arn
        FullRepositoryId = "skehlet/dailymail"
        BranchName       = "main"
      }
      run_order = 1
    }
  }


  stage {
    name = "CreateImage"
    action {
      name            = "CreateImage"
      namespace       = "CreateImage"
      input_artifacts = ["SourceArtifact"]
      category        = "Build"
      provider        = "CodeBuild"
      owner           = "AWS"
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.create_image.name
        EnvironmentVariables = jsonencode([
          { "name" : "PIPELINE_EXECUTION_ID", "value" : "#{codepipeline.PipelineExecutionId}" },
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
          { "name" : "PIPELINE_EXECUTION_ID", "value" : "#{codepipeline.PipelineExecutionId}" },
          { "name" : "IMAGE_URI", "value" : "#{CreateImage.IMAGE_URI}" },
        ])
      }
      run_order = 3
    }
  }
}



resource "aws_codebuild_project" "create_image" {
  name          = "${local.pipeline_name}-CreateImage"
  description   = "Create shared Lambda image"
  build_timeout = 15
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "cicd/app/buildspecs/buildspec-create-image.yaml"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    type            = "ARM_CONTAINER"
    image           = "aws/codebuild/amazonlinux2-aarch64-standard:3.0"
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
    type         = "ARM_CONTAINER"
    image        = "aws/codebuild/amazonlinux2-aarch64-standard:3.0"
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
