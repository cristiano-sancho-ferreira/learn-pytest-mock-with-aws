#################
# SDLF
# Modelo => https://github.com/slalompdx/terraform-aws-codecommit-cicd/blob/master/main.tf
# Outros exemplos:
# https://aws.amazon.com/pt/blogs/security/how-use-ci-cd-deploy-configure-aws-security-services-terraform/
# https://www.ioconnectservices.com/insight/aws-with-terraform#:~:text=Use%20CodeBuild%20within%20CodePipeline%20to,change%20in%20the%20Terraform%20file.
# Video -> https://www.youtube.com/watch?v=JwTP3wZHYnU
#          https://www.youtube.com/watch?v=zTQ1kY8xsY8
#          https://www.youtube.com/watch?v=PnGqOnp6mE4

# https://github.com/Abdel-Raouf/terraform-aws-codepipeline-ci-cd/blob/master/modules/codepipeline/iam.tf
#################
data "aws_caller_identity" "current" {} 
data "aws_region" "current" {}

/*
resource "aws_dynamodb_table" "tf_state_lock_github" {
  name         = "tf-state-lock-dynamo-github"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  tags = var.common_tags
}
*/

##############################################
# CodeBuild Section for the Test stage
##############################################
resource "aws_codebuild_project" "build_project" {
  name          = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "build-github"])
  description   = "The CodeBuild project for ${var.organization_name}"
  service_role  = aws_iam_role.codebuild_assume_role.arn
  build_timeout = var.build_timeout

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type    = var.build_compute_type
    image           = var.build_image
    type            = "LINUX_CONTAINER"
    privileged_mode = var.build_privileged_override

    environment_variable {
      name  = "TF_COMMAND"
      value = "apply"
      type  = "PLAINTEXT"
    } 
    
    environment_variable {
      name  = "ORG"
      value = var.organization_name  # aws_iam_access_key.ci_cd_access_key.id # Access Key da Conta B
    } 
    
    environment_variable {
      name  = "ACCOUNT"
      value = data.aws_caller_identity.current.account_id
    }
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/${var.vcs_repo.identifier}.git"
    git_clone_depth = 1

    buildspec = var.package_buildspec

    git_submodules_config {
      fetch_submodules = true
    }
  }

  tags = var.common_tags
}

##############################################
# CodeBuild Section for the Test stage
##############################################
resource "aws_codebuild_project" "build_project_prod" {
  name          = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "build-github-cross"])
  description   = "The CodeBuild project for ${var.organization_name}"
  service_role  = aws_iam_role.codebuild_assume_role.arn
  build_timeout = var.build_timeout

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type    = var.build_compute_type
    image           = var.build_image
    type            = "LINUX_CONTAINER"
    privileged_mode = var.build_privileged_override

    environment_variable {
      name  = "TF_COMMAND"
      value = "apply"
      type  = "PLAINTEXT"
    } 
    
    environment_variable {
      name  = "AWS_ACCESS_KEY_ID"
      # aws_iam_access_key.ci_cd_access_key.id # Access Key da Conta B
      value = "secrets-manager:${aws_secretsmanager_secret.ci_cd_credentials.arn}:access_key" 
    }

    environment_variable {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = "secrets-manager:${aws_secretsmanager_secret.ci_cd_credentials.arn}:secret_key"
      # aws_iam_access_key.ci_cd_access_key.secret # Secret Key da Conta B
    }
    
    environment_variable {
      name  = "ORG"
      value = var.organization_name  # aws_iam_access_key.ci_cd_access_key.id # Access Key da Conta B
    }
    
    environment_variable {
      name  = "ACCOUNT"
      value = data.aws_caller_identity.current.account_id
    }

  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/${var.vcs_repo.identifier}.git"
    git_clone_depth = 1

    buildspec = "buildspec-prd.yaml"

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

  tags = var.common_tags
}

# CodeBuild IAM Permissions
resource "aws_iam_role" "codebuild_assume_role" {
  name               = "${var.organization_name}-${var.application_name}-codebuild-role-github"
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
  name = "${var.organization_name}-${var.application_name}-codebuild-policy-github"
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
        "${aws_codebuild_project.build_project.id}"
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
        "logs:PutLogEvents"
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


resource "aws_iam_role_policy_attachment" "name1" {
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  #policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
  role = aws_iam_role.codebuild_assume_role.id
}

resource "aws_iam_role_policy_attachment" "name2" {
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
  tags     = var.common_tags

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
    name = "Build-Dev"

    action {
      name             = "Build-Dev1"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output1"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.build_project.name
      }
    }
  }

  stage {
    name = "Approval"
    action {
      name     = "ManualApproval"
      category = "Approval"
      owner    = "AWS"
      provider = "Manual"
      version  = "1"

      configuration = {
        CustomData      = "Aprovação necessária antes da implantação"
        #NotificationArn = aws_sns_topic.approval_topic.arn  # Tópico SNS para notificar por e-mail
      }
    }
  }

  stage {
    name = "Build-Prod"

    action {
      name             = "Build-Prod1"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output2"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.build_project_prod.name
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
  name = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "pipeline-role-github"])

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
  name = join("-", [var.organization_name, var.application_name, var.environment, data.aws_region.current.name, data.aws_caller_identity.current.account_id, "pipeline-policy-github"])
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


resource "aws_secretsmanager_secret" "ci_cd_credentials" {
  name = join("-", [var.organization_name, var.application_name, var.environment, "ci-cd-credentials"])
}

resource "aws_secretsmanager_secret_version" "ci_cd_credentials_version" {
  secret_id = aws_secretsmanager_secret.ci_cd_credentials.id
  secret_string = jsonencode({
    access_key = var.aws_access_key_id
    secret_key = var.aws_secret_access_key
  })
}

