terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    bucket = "always-upgrade-terraform-state"
    key    = "clearskies.info.json"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}
