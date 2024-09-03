#############################################################################
# Pipeline - "Contains Lambda"
######################## Parameters Store Values ########################
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  lambda_runtime = var.lambda_runtime
  lambda_handler = "lambda_function.lambda_handler"
}


resource "aws_iam_role" "routing" {
  name                 = "pytest-${var.environment}-routing-a"
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
  depends_on           = [aws_iam_role.step5]
}

resource "aws_iam_role_policy_attachment" "routing" {
  role       = aws_iam_role.routing.name
  policy_arn = aws_iam_policy.lambda_common.arn
}

resource "aws_iam_role_policy" "routing" {
  name   = "pytest-${var.environment}-mock-a"
  role   = aws_iam_role.routing.id
  policy = data.aws_iam_policy_document.routing.json
}

data "aws_iam_policy_document" "routing" {
  statement {
    actions = [
      "states:StartExecution"
    ]
    resources = [
      aws_sfn_state_machine.this.arn
    ]
  }
}



data "archive_file" "routing" {
  type        = "zip"
  source_file = "../app/src/lambda_function.py"
  output_path = "../app/src/lambda_function.zip"
}

resource "aws_lambda_function" "routing" {
  function_name    = join("-", ["pytest", var.environment, "routing-a"])
  description      = "File to test with pytestusing AWS Lambda"
  role             = aws_iam_role.routing.arn
  handler          = local.lambda_handler
  runtime          = var.lambda_runtime
  memory_size      = 128
  timeout          = 60
  source_code_hash = data.archive_file.routing.output_base64sha256
  filename         = data.archive_file.routing.output_path
  tags             = var.common_tags
}

