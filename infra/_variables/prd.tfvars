region                 = "us-east-1"
environment            = "prd"
lambda_runtime         = "python3.11"
common_tags = {
  "Name"    = "SDLF"
  "Projeto" = "AWS with Terraform"
  "Fase"    = "Data Lake"
}
application = "generation-json"
