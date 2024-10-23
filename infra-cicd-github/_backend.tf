# Centralizar o arquivo de controle de estado do terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.70.0"
    }
  }
  backend "s3" {
    bucket = "${var.organization_name}-terraform-state"
    key    = "state/aws/cicd-github/terraform.tfstate"
    region = "us-east-1"
  }
}
