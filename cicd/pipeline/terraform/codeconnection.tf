resource "aws_codeconnections_connection" "dailymail_github" {
  name          = "DailyMailGithub"
  provider_type = "GitHub"
}
