variable "region" {
  description = "The AWS region to deploy resources"
  type        = string
}

variable "common_tags" {
  description = "Common tags of the project"
  type        = map(string)
}


variable "organization_name" {
  description = "Name of the organization"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}


variable "application_name" {
  description = "Name of the application"
  type        = string
}


variable "repo_default_branch" {
  description = "Name of the branch repository"
  type        = string
  default     = "main"
}


variable "package_buildspec" {
  description = "The buildspec to be used for the Package stage (default: buildspec.yml)"
  type        = string
}


variable "build_privileged_override" {
  description = "Set the build privileged override to 'true' if you are not using a CodeBuild supported Docker base image. This is only relevant to building Docker images"
  default     = "false"
}

variable "build_timeout" {
  description = "The time to wait for a CodeBuild to complete before timing out in minutes (default: 5)"
  type        = string
}


variable "build_compute_type" {
  description = "The build instance type for CodeBuild (default: BUILD_GENERAL1_SMALL)"
  type        = string
}


variable "build_image" {
  description = "The build image for CodeBuild to use (default: aws/codebuild/nodejs:6.3.1)"
  type        = string
}

variable "force_artifact_destroy" {
  description = "Force the removal of the artifact S3 bucket on destroy (default: false)."
  default     = "true"
}

variable "artifact_type" {
  default     = "CODEPIPELINE"
  description = "The build output artifact's type. Valid values for this parameter are: CODEPIPELINE, NO_ARTIFACTS or S3."
}

variable "vcs_repo" {
  type = object({ identifier = string, branch = string })
}