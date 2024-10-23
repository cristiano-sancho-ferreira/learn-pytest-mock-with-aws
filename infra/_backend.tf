# Centralizar o arquivo de controle de estado do terraform
data "aws_caller_identity" "current" {}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.35.0"
    }
  }
  
  backend "s3" {
    bucket = "${var.organization_name}-${data.aws_caller_identity.current.account_id}-terraform-state"
    key    = "state/aws/sdlf/generation-json/terraform.tfstate"
    region = "us-east-1"
  }
}