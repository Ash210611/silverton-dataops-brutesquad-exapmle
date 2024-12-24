locals {
  branch_suffix   = terraform.workspace != "default" ? lower(terraform.workspace) : local.account_env_name
  param_store_env = data.aws_ssm_parameter.env.value
  account_env_name = lower(
    element(
      split("-", data.aws_iam_account_alias.current.account_alias), length(split("-", data.aws_iam_account_alias.current.account_alias)) - 1
    )
  )

  s3_airflow = data.terraform_remote_state.maa_s3.outputs.global_airflow_bucket
  yaml_data  = merge({tdv_dml=[]},{tdv_ddl=[]},{ddl=[]},{dml_with_dag=[]},{stored_proc=[]},
    yamldecode(file("../../../solution_repo_config.yaml")))
}
