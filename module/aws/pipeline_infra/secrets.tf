locals {
  ## if ops_branch != 'main' then -ops_branch else ""
  ops_branch_suffix = replace(var.branch_name, "feature_", "") == "main" ? "" : "-${replace(var.branch_name, "feature_", "")}"
  solutions_branch_suffix = terraform.workspace != "default" ? "-${lower(terraform.workspace)}" : ""

#  sm_suffix = "-${var.solution_repo}${local.ops_branch_suffix}"
  sm_suffix = "-${var.solution_repo}${local.solutions_branch_suffix}"
  sm_prefix = "maa-tdv-sa-"

  secrets_list = [
    {
      user = var.tdv_sa_username_1
      pass = var.tdv_sa_password_1
    },
    {
      user = var.tdv_sa_username_2
      pass = var.tdv_sa_password_2
    },
    {
      user = var.tdv_sa_username_3
      pass = var.tdv_sa_password_3
    }
  ]


  ## list of secrets created
  sm_outputs_all = toset([
    for s in module.tdv_secrets_manager : s.name
  ])

  ## secret that matches specified tdv_env
  regex_match = upper(var.tdv_env)
  matching_element = [for item in local.sm_outputs_all : item if length(regexall("(${local.regex_match})([^\\w]|$)", item)) > 0]
}

module "tdv_secrets_manager" {
  for_each = {for secret in distinct(local.secrets_list) : secret.user => secret if secret.user!=""}

  source              = "git::https://github.sys.cigna.com/cigna/dae-terraform-modules.git//modules/secrets"
  secret_manager_name = "${local.sm_prefix}${each.value.user}${local.sm_suffix}"
  secret_map = {
    username = "${each.value.user}"
    password = "${each.value.pass}"
  }
  kms_key_alias = data.terraform_remote_state.maa_kms.outputs.secretmanager_key_alias_arn
  master_tags   = merge({tdv_env=lower(replace(each.value.user,"SVT_DATAOPS_",""))}, module.pipeline_tag.additional_tags, module.pipeline_tag.required_tags)
  server_tags   = module.pipeline_tag.data_tags_only
}