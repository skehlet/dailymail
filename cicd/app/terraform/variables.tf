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

variable "scraper_batch_size" {
  type = number
  description = "How many events to batch to a single lambda invocation, default 10"
  default = 10
}
