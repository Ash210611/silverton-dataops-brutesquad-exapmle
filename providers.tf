terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.44.0"
    }
  }

  backend "s3" {}

}

provider "aws" {

  default_tags {
    tags = {
      CostCenter       = "12HS0285"
      AssetOwner       = "TCS"
      SecurityReviewID = "notAssigned"
    }
  }

  region = var.region
}
