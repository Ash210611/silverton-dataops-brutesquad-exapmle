data "aws_iam_account_alias" "current" {}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

module "tdv_ddl" {
  source    = "./modules/tdv"
  for_each  = { for x in local.yaml_data["tdv_ddl"] : x.name => x }
  repo_path = var.repo_path

  branch        = local.branch_suffix
  dest_bucket   = local.s3_airflow
  type          = "tdv_ddl"
  type_map      = each.value
  solution_repo = var.solution_repo
  env           = local.param_store_env
  tdv_env       = var.tdv_env
}

module "tdv_dml" {
  source    = "./modules/tdv"
  for_each  = { for x in local.yaml_data["tdv_dml"] : x.name => x }
  repo_path = var.repo_path

  branch        = local.branch_suffix
  dest_bucket   = local.s3_airflow
  type          = "tdv_dml"
  type_map      = each.value
  solution_repo = var.solution_repo
  env           = local.param_store_env
  tdv_env       = var.tdv_env
}

module "dml_with_dag" {
  source    = "./modules/tdv"
  for_each  = { for x in local.yaml_data["dml_with_dag"] : x.name => x }
  repo_path = var.repo_path

  branch        = local.branch_suffix
  dest_bucket   = local.s3_airflow
  type          = "dml_with_dag"
  type_map      = each.value
  solution_repo = var.solution_repo
  env           = local.param_store_env
  tdv_env       = var.tdv_env
}

module "stored_procs" {
  source    = "./modules/tdv"
  for_each  = { for x in local.yaml_data["stored_proc"] : x.name => x }
  repo_path = var.repo_path

  branch        = local.branch_suffix
  dest_bucket   = local.s3_airflow
  type          = "stored_proc"
  type_map      = each.value
  solution_repo = var.solution_repo
  env           = local.param_store_env
  tdv_env       = var.tdv_env
}
