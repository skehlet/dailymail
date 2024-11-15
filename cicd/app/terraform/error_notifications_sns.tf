resource "aws_sns_topic" "error_notifications" {
  name = "${local.app_id}-ErrorNotifications"
}
