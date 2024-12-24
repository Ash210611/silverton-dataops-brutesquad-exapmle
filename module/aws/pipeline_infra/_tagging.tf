module "pipeline_tag" {
  source      = "git::https://github.sys.cigna.com/cigna/dae-terraform-modules.git//modules/tagging"
  env         = data.aws_ssm_parameter.env.value
  platform    = "Medicare Advantage Analytics"
  source_repo = var.solution_repo
  additional_tags = {
    SecurityReviewID = var.security_review_id
  }
}
