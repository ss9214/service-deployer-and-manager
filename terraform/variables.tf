variable "aws_access_key" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "platform_name" {
  description = "Name for the deployment platform"
  type        = string
  default     = "deployer"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "ec2_instance_type" {
  description = "EC2 instance type for Kubernetes cluster"
  type        = string
  default     = "t3.medium"
}

variable "ssh_key_name" {
  description = "Name of AWS SSH key pair (optional)"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = true
}
