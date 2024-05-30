resource "aws_lambda_function" "rss_reader" {
  function_name = "dailymail-rss-reader"
  package_type  = "Image"
  image_uri     = var.image_uri
  role          = aws_iam_role.rss_reader.arn
  timeout       = 180
  memory_size   = 512
  handler       = "index.handler"
  #   environment {
  #     variables = {
  #       foo = "bar"
  #     }
  #   }
  depends_on = [
    aws_cloudwatch_log_group.rss_reader_logs,
  ]
}

resource "aws_cloudwatch_log_group" "rss_reader_logs" {
  name              = "/aws/lambda/dailymail-rss-reader"
  retention_in_days = 7
}









# resource "aws_lambda_permission" "allow_cloudwatch" {
#   statement_id  = "AllowExecutionFromCloudWatch"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.test_lambda.function_name
#   principal     = "events.amazonaws.com"
#   source_arn    = "arn:aws:events:eu-west-1:111122223333:rule/RunDaily"
#   qualifier     = aws_lambda_alias.test_alias.name
# }
