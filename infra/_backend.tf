# Centralizar o arquivo de controle de estado do terraform

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.35.0"
    }
  }
  /*
  backend "s3" {
    bucket = "${var.organization_name}-${var.number_account_id}-terraform-state"
    key    = "state/aws/sdlf/generation-json/terraform.tfstate"
    region = "us-east-1"
  }*/
}