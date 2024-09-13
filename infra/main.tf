#############################################################################
# Pipeline - "Contains Lambda"
######################## Parameters Store Values ########################
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  lambda_runtime = var.lambda_runtime
  lambda_handler = "lambda_function.lambda_handler"
}


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}
resource "aws_iam_role" "lambda_role" {
  name               = "lambda-s3-sqs-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# Políticas para a função Lambda acessar SQS e S3
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda-s3-sqs-policy"
  description = "Permitir acesso ao S3 e SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.bucket.arn}/*",
          "${aws_s3_bucket.bucket.arn}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = "${aws_sqs_queue.file_queue.arn}"
      },
      {
        Effect = "Allow"
        Action = [
        "logs:CreateLogStream",
        "logs:CreateLogGroup",
        "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}


/*
resource "aws_iam_role_policy_attachment" "iam_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"                
  role = aws_iam_role.lambda_role.id
}


resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generation_json.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}*/


data "archive_file" "xlrd-120" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-layer/xlrd-120/src"
  output_path = "${path.module}/lambda-layer/xlrd-120/xlrd-120.zip"
}

resource "aws_lambda_layer_version" "xlrd-120" {
  filename            = data.archive_file.xlrd-120.output_path
  layer_name          = "xlrd-120"
  source_code_hash    = data.archive_file.xlrd-120.output_base64sha256
  compatible_runtimes = [var.lambda_runtime]
  description         = "Contains the latest version xlrd 1.2.0 and openpyxl"
}


data "archive_file" "generation_json" {
  type        = "zip"
  source_file = "../app/src/lambda_function.py"
  output_path = "../app/src/lambda_function.zip"
}

resource "aws_lambda_function" "generation_json" {
  function_name    = join("-", ["pytest", var.environment, var.application])
  description      = "File to test with pytest using AWS Lambda"
  role             = aws_iam_role.lambda_role.arn
  handler          = local.lambda_handler
  runtime          = var.lambda_runtime
  memory_size      = 128
  timeout          = 60
  source_code_hash = data.archive_file.generation_json.output_base64sha256
  filename         = data.archive_file.generation_json.output_path
  layers = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python311:17", aws_lambda_layer_version.xlrd-120.arn]
  tags             = var.common_tags

  environment {
    variables = {
      OUTPUT_BUCKET = aws_s3_bucket.bucket.bucket
      SQS_NAME = aws_sqs_queue.file_queue.name
      ACCOUNT_ID = data.aws_caller_identity.current.account_id
    }
  }
}


resource "aws_s3_bucket" "bucket" {
  bucket        =  "teste-543543265465-sancho"
  force_destroy = "true"
}


resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  queue {
    queue_arn     = aws_sqs_queue.file_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix       = "Mapeamento_"
  }
  #depends_on = [aws_lambda_permission.allow_bucket]
}

/*
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.generation_json.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "Mapeamento_"
    filter_suffix       = ".xlsx"
  }

}
*/


# Fila SQS
resource "aws_sqs_queue" "file_queue" {
  name = "s3-event-notification-queue"
  visibility_timeout_seconds   = 300
  message_retention_seconds    = 86400
  receive_wait_time_seconds    = 10


  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:*:*:s3-event-notification-queue",
      "Condition": {
        "ArnEquals": { "aws:SourceArn": "${aws_s3_bucket.bucket.arn}" }
      }
    }
  ]
}
POLICY
}


# Configurando o Lambda para ser disparado pela fila SQS
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.file_queue.arn
  function_name    = aws_lambda_function.generation_json.arn
  batch_size       = 1
}




