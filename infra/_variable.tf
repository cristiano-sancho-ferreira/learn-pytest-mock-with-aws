variable "region" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

variable "environment" {
  type = string
}

variable "lambda_runtime" {
  type = string
}

variable "application" {
  type = string
}
