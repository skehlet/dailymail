variable "image_uri" {
  type        = string
  description = "URI of ECR image"
  nullable    = false
}

variable "build_id" {
  type = string
  description = "The build id"
  nullable = false
}
