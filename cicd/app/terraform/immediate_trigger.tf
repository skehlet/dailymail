resource "aws_lambda_event_source_mapping" "immediate_trigger" {
  batch_size                         = var.immediate_trigger_batch_size
  maximum_batching_window_in_seconds = var.immediate_trigger_maximum_batching_window_in_seconds
  event_source_arn                   = aws_sqs_queue.immediate_queue.arn
  function_name                      = aws_lambda_function.immediate.arn
  scaling_config {
    maximum_concurrency = 10
  }
}
