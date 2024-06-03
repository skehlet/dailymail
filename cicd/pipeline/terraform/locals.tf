locals {
  pipeline_name = "DailyMailPipeline"
  ecr_repos     = [
    "dailymail-rss-reader",
    "dailymail-scraper",
    "dailymail-summarizer",
  ]
}
