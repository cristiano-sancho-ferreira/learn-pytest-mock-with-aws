#################
# SDLF
#################
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}


##############################################
# CodeBuild Section for the account Developer
##############################################
resource "aws_codebuild_project" "build_dev_stage1" {
  name          = join("-", [var.organization_name, var.application_name, var.environment, data.aws_caller_identity.current.account_id, "build-github-dev-stage1"])
  description   = "The CodeBuild project for ${var.organization_name}"
  service_role  = aws_iam_role.codebuild_assume_role.arn
  build_timeout = var.build_timeout

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type    = var.build_compute_type
    image           = var.build_image
    type            = var.build_type
    privileged_mode = var.build_privileged_override

    environment_variable {
      name  = "TF_VERSION"
      value = var.terraform_version
      type  = "PLAINTEXT"
    }
    environment_variable {
      name  = "TF_COMMAND"
      value = var.terraform_action
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "ORG"
      value = var.organization_name
      type  = "PLAINTEXT"
    }
    
    environment_variable {
      name  = "ENV"
      value = var.account_env
      type  = "PLAINTEXT"
    }    
    
    environment_variable {
      name  = "ACCOUNT_ASSUME_ROLE"
      value = var.account_assume_role
      type  = "PLAINTEXT"
    }

    environment_variable {
      # Access Key da Conta Production
      name  = "ACCESS_KEY_ID"
      value = aws_ssm_parameter.account1_access_key_id.name
      #value = var.aws_access_key_id
      type = "PARAMETER_STORE"
    }

    environment_variable {
      # Secret Key da Conta Production
      name  = "SECRET_ACCESS_KEY"
      value = aws_ssm_parameter.account1_secret_access_key.name
      #value = var.aws_secret_access_key
      type = "PARAMETER_STORE"
    }
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/${var.vcs_repo.identifier}.git"
    git_clone_depth = 1

    buildspec = "buildspec.yaml"

    git_submodules_config {
      fetch_submodules = true
    }
  }

  tags = var.common_tags
}




# CodePipeline resources
resource "aws_s3_bucket" "build_artifact_bucket" {
  bucket = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "build-github"])
  #acl           = "private"
  force_destroy = var.force_artifact_destroy
  tags          = var.common_tags
}


# CodeBuild IAM Permissions
resource "aws_iam_role" "codebuild_assume_role" {
  name               = "${var.organization_name}-${var.application_name}-codebuild-github-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy" "codebuild_policy" {
  name = "${var.organization_name}-${var.application_name}-codebuild-github-policy"
  role = aws_iam_role.codebuild_assume_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
       "s3:PutObject",
       "s3:GetObject",
       "s3:GetObjectVersion",
       "s3:GetBucketVersioning"
      ],
      "Resource": [
        "${aws_s3_bucket.build_artifact_bucket.arn}",
        "${aws_s3_bucket.build_artifact_bucket.arn}/*"
      ],
      "Effect": "Allow"
    },
    {
      "Effect": "Allow",
      "Resource": [
        "${aws_codebuild_project.build_dev_stage1.id}"
      ],
      "Action": [
        "codebuild:*"
      ]
    },
    {
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Action": [
        "lakeformation:PutDataLakeSettings",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "secretsmanager:GetSecretValue",
        "ssm:GetParameter",
        "ssm:GetParameters"
      ]
    },
    {
      "Action": [
        "kms:DescribeKey",
        "kms:GenerateDataKey*",
        "kms:Encrypt",
        "kms:ReEncrypt*",
        "kms:Decrypt"
      ],
      "Resource": [
        "*"
      ],
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy" "cross_account" {
  name = join("-", [var.organization_name, var.application_name, "cross-account-policy"])
  role = aws_iam_role.codebuild_assume_role.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AssumeRole01",
        "Effect" : "Allow",
        "Action" : "sts:AssumeRole",
        "Resource" : [
          for account_id in var.target_account_ids : "arn:aws:iam::${account_id}:role/sdlf-cross-account"
        ]
      }
    ]
  })
}



resource "aws_iam_role_policy_attachment" "name1" {
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  role       = aws_iam_role.codebuild_assume_role.id
}


####################################################
# Connections GitHub
####################################################
# a CodeStarConnections connection manages access to GitHub (so you do not need to use a private access token).
resource "aws_codestarconnections_connection" "github" {
  name          = join("-", [var.organization_name, var.application_name, "connection-github"])
  provider_type = "GitHub"
}


####################################################
# Full CodePipeline
####################################################
resource "aws_codepipeline" "codepipeline" {
  name     = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "pipeline-github"])
  role_arn = aws_iam_role.codepipeline_role.arn
  #pipeline_type = V2
  tags = var.common_tags

  artifact_store {
    location = aws_s3_bucket.codepipeline_bucket.bucket
    type     = "S3"

  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        FullRepositoryId = var.vcs_repo.identifier
        BranchName       = var.vcs_repo.branch
        # Source fetches code from GitHub using CodeStar.
        ConnectionArn = aws_codestarconnections_connection.github.arn
      }
    }
  }

  stage {
    name = "Deploy-Development"

    action {
      name             = "Build-Dev-StageA"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output_1"]
      version          = "1"
      run_order        = 1

      configuration = {
        ProjectName = aws_codebuild_project.build_dev_stage1.name
      }
    }
  }
}

resource "aws_s3_bucket" "codepipeline_bucket" {
  bucket = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "pipeline-github"])
  #acl    = "private"
  force_destroy = "true"
  tags          = var.common_tags

}

resource "aws_s3_bucket_lifecycle_configuration" "codepipeline_bucket" {
  bucket = aws_s3_bucket.codepipeline_bucket.id
  rule {
    id     = "sdlf-lifecycle-codepipeline"
    status = "Enabled"

    filter {}

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    expiration {
      days = 60
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

resource "aws_iam_role" "codepipeline_role" {
  name = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "pipeline-github-role"])

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "pipeline-github-policy"])
  role = aws_iam_role.codepipeline_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": [
        "${aws_s3_bucket.codepipeline_bucket.arn}",
        "${aws_s3_bucket.codepipeline_bucket.arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild",
        "codebuild:ListConnectedOAuthAccounts",
        "codebuild:ListRepositories",
        "codebuild:PersistOAuthToken",
        "codebuild:ImportSourceCredentials"
      ],
      "Resource": "*"
    },
      {
          "Effect": "Allow",
          "Action": [
              "codestar-connections:UseConnection"
          ],
          "Resource": "${aws_codestarconnections_connection.github.arn}"
      }
  ]
}
EOF
}

/*
resource "aws_secretsmanager_secret" "ci_cd_credentials" {
  name = join("-", [var.organization_name, var.application_name, var.environment, "ci-cd-credentials"])
}


resource "aws_secretsmanager_secret_version" "ci_cd_credentials_version" {
  secret_id = aws_secretsmanager_secret.ci_cd_credentials.id
  secret_string = jsonencode({
    access_key = var.aws_access_key_id
  })
}
*/

# Criar o Parameter Store para Access Key e Secret Key para contas DEV e PROD
resource "aws_ssm_parameter" "account1_access_key_id" {
  name        = "/SDLF/${var.organization_name}/development/access_key_id"
  description = "AWS Access Key ID for my application"
  type        = "SecureString"
  value       = var.account1_access_key_id
}

resource "aws_ssm_parameter" "account1_secret_access_key" {
  name        = "/SDLF/${var.organization_name}/development/secret_access_key"
  description = "AWS Secret Access Key for my application"
  type        = "SecureString"
  value       = var.account1_secret_access_key
}






