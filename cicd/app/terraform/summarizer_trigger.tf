resource "aws_s3_bucket_notification" "summarizer_trigger" {
  bucket = aws_s3_bucket.summarizer.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.summarizer.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "incoming/"
  }
  depends_on = [
    aws_lambda_permission.summarizer_allow_bucket_notifications
  ]
}
