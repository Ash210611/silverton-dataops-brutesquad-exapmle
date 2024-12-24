variable "region" {}

variable "repo_path" {
  type = string
}

variable "solution_repo" {
  type = string
}

variable "tdv_env" {}

variable "security_review_id" {
  description = "Security Review ID of the project"
  type        = string
}

variable "branch_name" {
  description = "branch name of the ops repo"
  type        = string
}

variable "tdv_sa_username_1" {
  description = "user name 1 of TDV access"
  type        = string
}

variable "tdv_sa_password_1" {
  description = "password 1 of TDV access"
  type        = string
}

variable "tdv_sa_username_2" {
  description = "user name 2 of TDV access"
  type        = string
  default     = ""
}

variable "tdv_sa_password_2" {
  description = "password 2 of TDV access"
  type        = string
  default     = ""
}

variable "tdv_sa_username_3" {
  description = "user name 3 of TDV access"
  type        = string
  default     = ""
}

variable "tdv_sa_password_3" {
  description = "password 3 of TDV access"
  type        = string
  default     = ""
}
