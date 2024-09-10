#############################################################################
# Pipeline - "Contains Lambda"
######################## Parameters Store Values ########################
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  lambda_runtime = var.lambda_runtime
  lambda_handler = "lambda_function.lambda_handler"
}



resource "aws_iam_policy" "lambda_common" {
  name   = "sdlf-${var.environment}-${var.application}-common-a"
  policy = data.aws_iam_policy_document.lambda_common.json
  tags   = var.common_tags
}

data "aws_iam_policy_document" "lambda_common" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
    ]
  }
  statement {
    actions = [
      "logs:CreateLogGroup"
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/sdlf-${var.environment}-${var.application}-*"
    ]
  }
  statement {
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters"
    ]
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/SDLF/*"
    ]
  }
}



resource "aws_iam_role" "generation_json" {
  name                 = "pytest-${var.environment}-${var.application}-a"
  #permissions_boundary = var.permissions_boundary_managed_policy
  path                 = "/state-machine/"
  tags                 = var.common_tags
  assume_role_policy   = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "generation_json" {
  role       = aws_iam_role.generation_json.name
  policy_arn = aws_iam_policy.lambda_common.arn
}


data "archive_file" "generation_json" {
  type        = "zip"
  source_file = "../app/src/lambda_function.py"
  output_path = "../app/src/lambda_function.zip"
}

resource "aws_lambda_function" "generation_json" {
  function_name    = join("-", ["pytest", var.environment, var.application])
  description      = "File to test with pytest using AWS Lambda"
  role             = aws_iam_role.generation_json.arn
  handler          = local.lambda_handler
  runtime          = var.lambda_runtime
  memory_size      = 128
  timeout          = 60
  source_code_hash = data.archive_file.generation_json.output_base64sha256
  filename         = data.archive_file.generation_json.output_path
  layers = [  ]
  tags             = var.common_tags
}

