terraform {
  backend "s3" {
    bucket = "ot-staging-terraform-remote-state"
    key    = "serverless/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "serverless-terraform-state-lock"
    profile = "otkhwae"
  }
}