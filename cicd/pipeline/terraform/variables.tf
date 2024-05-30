variable "slack_workspace_id" {
  type    = string
  default = "T4SF83P7Y" // luna cat
}

variable "slack_channel_id" {
  type    = string
  default = "C076JE32464" // #feed-main-pipeline
}

variable "codebuild_terraform_image_tag" {
  type = string
  description = "Tag of the codebuild-terraform-image in ECR"
  default = "5"
}
