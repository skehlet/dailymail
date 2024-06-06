locals {
  pipeline_name = "DailyMailPipeline"
  ecr_repos     = [
    "dailymail-rss-reader",
    "dailymail-link-reader",
    "dailymail-scraper",
    "dailymail-summarizer",
    "dailymail-digest",
  ]
}
