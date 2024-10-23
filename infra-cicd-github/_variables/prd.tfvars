region             = "us-east-1"
application_name   = "account"
organization_name  = "cross"
environment        = "prd"
package_buildspec  = "buildspec-dev.yaml"
build_timeout      = "15"
build_compute_type = "BUILD_GENERAL1_SMALL"
build_image        = "aws/codebuild/standard:7.0"
common_tags = {
  "Name"    = "SDLF"
  "Projeto" = "AWS with Terraform"
  "Fase"    = "CICD"
}
vcs_repo = {
  branch     = "main"
  identifier = "cristiano-sancho-ferreira/learn-pytest-mock-with-aws"
}
