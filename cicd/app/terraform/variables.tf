variable "rss_reader_image_uri" {
  type        = string
  description = "URI of RSS Reader ECR image"
  nullable    = false
}

variable "link_reader_image_uri" {
  type        = string
  description = "URI of Link Reader ECR image"
  nullable    = false
}

variable "scraper_image_uri" {
  type        = string
  description = "URI of Scraper ECR image"
  nullable    = false
}

variable "summarizer_image_uri" {
  type        = string
  description = "URI of Summarizer ECR image"
  nullable    = false
}

variable "digest_image_uri" {
  type        = string
  description = "URI of Digest ECR image"
  nullable    = false
}

variable "immediate_image_uri" {
  type        = string
  description = "URI of Immediate ECR image"
  nullable    = false
}

variable "build_id" {
  type = string
  description = "The build id"
  nullable = false
}

variable "scraper_trigger_batch_size" {
  type = number
  description = "How many events to batch to a single lambda invocation, AWS's default is 10"
  default = 10
}

variable "scraper_trigger_maximum_batching_window_in_seconds" {
  type = number
  description = "How long to wait to batch up events"
  default = 3
}

variable "summarizer_trigger_batch_size" {
  type = number
  description = "How many events to batch to a single lambda invocation, AWS's default is 10"
  default = 10
}

variable "summarizer_trigger_maximum_batching_window_in_seconds" {
  type = number
  description = "How long to wait to batch up events"
  default = 3
}

variable "immediate_trigger_batch_size" {
  type = number
  description = "How many events to batch to a single lambda invocation, AWS's default is 10"
  default = 10
}

variable "immediate_trigger_maximum_batching_window_in_seconds" {
  type = number
  description = "How long to wait to batch up events"
  default = 3
}
