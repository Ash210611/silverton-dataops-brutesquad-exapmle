output "maa_s3" {
  value = local.s3_airflow
}

output "yaml" {
  value = local.yaml_data
}

output "moduleyamlddl" {
  value = module.tdv_ddl
}

output "moduleyamldml" {
  value = module.tdv_dml
}

output "moduleyamlcustomdml" {
  value = module.dml_with_dag
}

output "moduleyamlsp" {
  value = module.stored_procs
}

output "aws_mwaa_environment_name" {
  value = data.terraform_remote_state.maa_mwaa.outputs.aws_mwaa_environment_name
}

output "env" {
  value     = local.param_store_env
  sensitive = true
}

output "aws_region" {
  value = data.aws_region.current.id
}

output "secrets_manager_list" {
  value = local.sm_outputs_all
}

output "secrets_name" {
  value = local.matching_element[0]
}



