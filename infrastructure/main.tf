# Configure the AWS Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">=1.2.0"
}

provider "aws" {
  region = var.region
}

### import from eks module
# module "eks" {
#   source = "./eks"
# }


### import from s3 module
# module "s3" {
#   source = "./do_not_destroy_setup/s3"
# }

### import from ecr module
# module "ecr" {
#   source = "./do_not_destroy_setup/ecr"
# }