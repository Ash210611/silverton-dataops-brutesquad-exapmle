variable "branch" {}

variable "repo_path" {
  type = string
}

variable "type" {
  type = string
}

variable "type_map" {
  type = object({
    name : string
    path-to-config : optional(string, "config")
    path-to-tables : optional(string, "tables")
    path-to-views : optional(string, "views")
    path-to-changelog : optional(string, "")
    s3-prefix : optional(string)
  })
}

variable "dest_bucket" {}

variable "solution_repo" {
  type = string
}

variable "env" {
  type = string
}

variable "tdv_env" {
  type = string
  default = ""
}

variable "tdv_environments" {
  type = map(list(string))
  default = {
    dev = ["dev", "dev2"],
    test = ["uat", "int", "qa"],
    prod = ["prd"]
  }
}