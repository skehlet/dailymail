locals {
  pipeline_name = "DailyMailPipeline"
  ecr_repos = [
    "dailymail-rss-reader",
    "dailymail-link-reader",
    "dailymail-email-reader",
    "dailymail-scraper",
    "dailymail-summarizer",
    "dailymail-digest",
    "dailymail-immediate",
  ]
}
