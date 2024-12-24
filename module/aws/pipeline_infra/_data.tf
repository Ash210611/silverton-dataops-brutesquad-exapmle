data "aws_ssm_parameter" "env" {
  name = "/Enterprise/Environment"
}

data "terraform_remote_state" "maa_s3" {
  backend = "s3"
  config = {
    bucket  = "cigna-tf-state-${data.aws_caller_identity.current.account_id}"
    key     = "terraform/maa/platform/${data.aws_region.current.id}/s3/${local.param_store_env}-tfstate"
    region  = "us-east-1"
    profile = "saml"
  }
}

data "terraform_remote_state" "maa_mwaa" {
  backend = "s3"
  config = {
    bucket  = "cigna-tf-state-${data.aws_caller_identity.current.account_id}"
    key     = "terraform/maa/platform/${data.aws_region.current.id}/airflow-env/${local.param_store_env}-tfstate"
    region  = "us-east-1"
    profile = "saml"
  }
}

data "terraform_remote_state" "maa_kms" {
  backend = "s3"
  config = {
    bucket  = "cigna-tf-state-${data.aws_caller_identity.current.account_id}"
    key     = "terraform/maa/platform/${data.aws_region.current.id}/kms/${local.param_store_env}-tfstate"
    region  = "us-east-1"
    profile = "saml"
  }
}
