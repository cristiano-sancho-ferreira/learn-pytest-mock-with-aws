provider "aws" {
  region = var.region
  assume_role {
    role_arn = "arn:aws:iam::${var.account_assume_role}:role/sdlf-cross-account"
  }
}
