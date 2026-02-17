variable "platform_name" {
  description = "Platform name for resource naming"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

# Security group for Kubernetes cluster
resource "aws_security_group" "k8s" {
  name        = "${var.platform_name}-k8s-sg"
  description = "Security group for Kubernetes cluster"
  vpc_id      = var.vpc_id

  # SSH access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes API
  ingress {
    description = "Kubernetes API"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # ArgoCD UI
  ingress {
    description = "ArgoCD UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.platform_name}-k8s-sg"
  }
}

# Security group for RDS databases
resource "aws_security_group" "rds" {
  name        = "${var.platform_name}-rds-sg"
  description = "Security group for RDS databases"
  vpc_id      = var.vpc_id

  # PostgreSQL
  ingress {
    description     = "PostgreSQL from K8s"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.k8s.id]
  }

  # MySQL
  ingress {
    description     = "MySQL from K8s"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.k8s.id]
  }

  # MongoDB
  ingress {
    description     = "MongoDB from K8s"
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.k8s.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.platform_name}-rds-sg"
  }
}

output "k8s_sg_id" {
  description = "Kubernetes security group ID"
  value       = aws_security_group.k8s.id
}

output "rds_sg_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}
