# Centralizar o arquivo de controle de estado do terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.70.0"
    }
  }
  backend "s3" {
    bucket = "devops-585008080757-terraform-state"
    key    = "sdlf/sdlf-cicd-github/terraform.tfstate"
    region = "us-east-1"
  }
}