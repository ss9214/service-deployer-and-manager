variable "platform_name" {
  description = "Platform name for resource naming"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for EC2 instance"
  type        = string
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = ""
}

# Latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User data script to install K3s
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Update system
    apt-get update
    apt-get upgrade -y

    # Install required packages
    apt-get install -y \
      curl \
      wget \
      git \
      jq \
      apt-transport-https \
      ca-certificates \
      software-properties-common

    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker ubuntu

    # Install K3s (lightweight Kubernetes)
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --disable traefik" sh -

    # Wait for K3s to be ready
    until kubectl get nodes; do
      echo "Waiting for K3s to be ready..."
      sleep 5
    done

    # Install Helm
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

    # Configure kubectl for ubuntu user
    mkdir -p /home/ubuntu/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
    chown -R ubuntu:ubuntu /home/ubuntu/.kube

    # Install nginx ingress controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/cloud/deploy.yaml

    # Save K3s token and config
    cp /var/lib/rancher/k3s/server/node-token /home/ubuntu/node-token
    chown ubuntu:ubuntu /home/ubuntu/node-token

    echo "K3s installation complete!" > /home/ubuntu/k3s-ready
  EOF
}

resource "aws_instance" "k8s" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids
  key_name               = var.key_name != "" ? var.key_name : null

  user_data = local.user_data

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "${var.platform_name}-k8s-master"
    Role = "kubernetes-master"
  }

  lifecycle {
    create_before_destroy = false
  }
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.k8s.id
}

output "instance_public_ip" {
  description = "EC2 instance public IP"
  value       = aws_instance.k8s.public_ip
}

output "cluster_endpoint" {
  description = "Kubernetes API endpoint"
  value       = "https://${aws_instance.k8s.public_ip}:6443"
}

output "cluster_ca_cert" {
  description = "Kubernetes cluster CA certificate (placeholder)"
  value       = "placeholder-ca-cert"
  sensitive   = true
}

output "cluster_token" {
  description = "Kubernetes cluster token (placeholder)"
  value       = "placeholder-token"
  sensitive   = true
}
