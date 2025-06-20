variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "meka-api"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "ses_from_email" {
  description = "Email address to send emails from (must be verified in SES)"
  type        = string
  default     = "noreply@yourdomain.com"
}
