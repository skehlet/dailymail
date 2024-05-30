terraform {
  backend "s3" {
    region         = "us-west-2"
    bucket         = "skehlet-terraformstate"
    dynamodb_table = "terraform-state"
    key            = "dailymail/pipeline.tfstate"
  }
}
