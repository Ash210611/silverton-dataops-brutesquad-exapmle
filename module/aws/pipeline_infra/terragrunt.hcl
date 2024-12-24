include {
  path = find_in_parent_folders()
}

locals {
  common_config = yamldecode(file("${get_terragrunt_dir()}/configs/configuration.yaml"))["${get_env("TF_VAR_project_name")}"]["${get_env("TF_VAR_region", "")}"]["common"]
  env_config    = yamldecode(file("${get_terragrunt_dir()}/configs/configuration.yaml"))["${get_env("TF_VAR_project_name")}"]["${get_env("TF_VAR_region", "")}"]["${get_env("TF_VAR_env", "dev")}"]
}

terraform {
  extra_arguments "load_common_config" {
    commands = [
      "init",
      "plan",
      "apply",
      "destroy"
    ]
    env_vars = { for k, v in local.common_config : "TF_VAR_${k}" => v }
  }

  extra_arguments "load_env_config" {
    commands = [
      "init",
      "plan",
      "apply",
      "destroy"
    ]
    env_vars = { for k, v in local.env_config : "TF_VAR_${k}" => v }
  }

  before_hook "before_hook_init_workspace" {
    commands =  ["plan", "state", "apply", "destroy", "refresh"]
    execute  = [
      "sh", "${get_parent_terragrunt_dir()}/../../commands/workspace.sh", "${get_env("TF_VAR_branch_workspace", "default")}"
    ]
  }

  after_hook "after_hook_destroy_workspace" {
    commands = ["destroy"]
    execute  = [
      "sh", "${get_parent_terragrunt_dir()}/../../commands/workspace_destroy.sh", "${get_env("TF_VAR_branch_workspace", "default")}"
    ]
  }

  extra_arguments "init" {
    commands  = ["init"]
    arguments = ["--reconfigure"]
  }

}
