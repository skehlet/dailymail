variable "rss_reader_image_uri" {
  type        = string
  description = "URI of RSS Reader ECR image"
  nullable    = false
}

variable "scraper_image_uri" {
  type        = string
  description = "URI of Scraper ECR image"
  nullable    = false
}

variable "build_id" {
  type = string
  description = "The build id"
  nullable = false
}
