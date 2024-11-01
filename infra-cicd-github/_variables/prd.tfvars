region             = "us-east-1"
organization_name  = "dragon"
environment        = "dev"
build_timeout      = "15"
build_compute_type = "BUILD_GENERAL1_SMALL"
build_image        = "aws/codebuild/standard:7.0"
build_type         = "LINUX_CONTAINER"
common_tags = {
  "Name"    = "SDLF"
  "Projeto" = "AWS with Terraform"
  "Fase"    = "CICD"
}
vcs_repo = {
  branch     = "main"
  identifier = "cristiano-sancho-ferreira/learn-pytest-mock-with-aws"
}
terraform_action = "destroy" # apply or destroy
terraform_version = "1.9.2"

target_account_ids = ["401932890892", "381491840841"]

account_assume_role = "381491840841"
account_env = "dev"



