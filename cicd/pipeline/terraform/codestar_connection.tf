resource "aws_codestarconnections_connection" "dailymail_github" {
  name          = "DailyMailGithub"
  provider_type = "GitHub"
}
