# Centralizar o arquivo de controle de estado do terraform

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.70.0"
    }
  }
  
   backend "s3" {
    #O backend será sobrescrito com o comando terraform init -backend-config
    # bucket = "devops-585008080757-terraform-state"
    # # bucket = "${var.organization_name}-${var.number_account_id}-terraform-state"
    # key    = "sdlf/generation-json/terraform.tfstate"
    # region = "us-east-1"
  }
}