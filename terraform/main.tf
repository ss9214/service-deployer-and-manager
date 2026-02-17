terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key

  default_tags {
    tags = {
      Project     = "service-deployer"
      ManagedBy   = "Terraform"
      Environment = "production"
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  platform_name = var.platform_name
  vpc_cidr      = var.vpc_cidr
}

# Security Groups
module "security" {
  source = "./modules/security"

  platform_name = var.platform_name
  vpc_id        = module.vpc.vpc_id
}

# EC2 + K3s Kubernetes Cluster
module "kubernetes" {
  source = "./modules/kubernetes"

  platform_name      = var.platform_name
  instance_type      = var.ec2_instance_type
  vpc_id             = module.vpc.vpc_id
  subnet_id          = module.vpc.public_subnet_ids[0]
  security_group_ids = [module.security.k8s_sg_id]
  key_name           = var.ssh_key_name
}

# ArgoCD Installation (runs after K3s is ready)
module "argocd" {
  source = "./modules/argocd"

  depends_on = [module.kubernetes]

  k8s_endpoint   = module.kubernetes.cluster_endpoint
  k8s_ca_cert    = module.kubernetes.cluster_ca_cert
  k8s_token      = module.kubernetes.cluster_token
  platform_name  = var.platform_name
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "ec2_instance_id" {
  description = "EC2 instance ID for K8s cluster"
  value       = module.kubernetes.instance_id
}

output "ec2_public_ip" {
  description = "EC2 instance public IP"
  value       = module.kubernetes.instance_public_ip
}

output "k8s_endpoint" {
  description = "Kubernetes API endpoint"
  value       = module.kubernetes.cluster_endpoint
}

output "argocd_url" {
  description = "ArgoCD web UI URL"
  value       = module.argocd.argocd_url
}

output "argocd_admin_password" {
  description = "ArgoCD admin initial password"
  value       = module.argocd.admin_password
  sensitive   = true
}

output "setup_complete" {
  description = "Infrastructure setup completion status"
  value       = true
}
