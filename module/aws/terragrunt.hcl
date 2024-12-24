generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${get_env("TF_VAR_region", "us-east-1")}"
}
EOF
}

// remote_state {
//   backend = "s3"
//   config  = {
//     bucket                   = "cigna-tf-state-${get_env("TF_VAR_account_number", "215132885729")}"
//     dynamodb_table           = "cigna-tf-lock-${get_env("TF_VAR_account_number", "215132885729")}"
//     key                      = "terraform/${get_env("TF_VAR_region", "us-east-1")}/${path_relative_to_include()}/${get_env("TF_VAR_solution_repo")}/${get_env("TF_VAR_env", "dev")}-tfstate"
//     # workspace_key_prefix = "workspace"
//     profile                  = "saml"
//     region                   = "${get_env("TF_VAR_region", "us-east-1")}"
//     skip_bucket_root_access  = true
//     skip_bucket_ssencryption = true
//     skip_bucket_enforced_tls = true
//   }
//   disable_dependency_optimization = true
// }

remote_state {
  backend = "s3"
  config = {
    disable_bucket_update = true
    bucket                = "silverton-tf-state-${get_env("TF_VAR_account_number")}-${get_env("TF_VAR_region")}"
    key                   = "northstar-sandbox/${path_relative_to_include()}/${get_env("TF_VAR_solution_repo")}/${get_env("TF_VAR_env", "dev")}/terraform.state"
    region                = "${get_env("TF_VAR_region", "us-east-1")}"
    dynamodb_table        = "silverton-tf-lock-${get_env("TF_VAR_account_number")}-${get_env("TF_VAR_region")}"
  }
  disable_dependency_optimization = true
}