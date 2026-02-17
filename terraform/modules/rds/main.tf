variable "platform_name" {
  description = "Platform name for resource naming"
  type        = string
}

variable "database_type" {
  description = "Database engine (postgres, mysql)"
  type        = string
  default     = "postgres"
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Database name"
  type        = string
}

variable "username" {
  description = "Master username"
  type        = string
}

variable "password" {
  description = "Master password"
  type        = string
  sensitive   = true
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for RDS subnet group"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.platform_name}-${var.database_name}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.platform_name}-${var.database_name}-subnet-group"
  }
}

resource "aws_db_instance" "main" {
  identifier     = "${var.platform_name}-${var.database_name}"
  engine         = var.database_type
  engine_version = var.database_type == "postgres" ? "16.1" : "8.0.35"

  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.database_name
  username = var.username
  password = var.password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  skip_final_snapshot       = true
  final_snapshot_identifier = "${var.platform_name}-${var.database_name}-final-snapshot"

  enabled_cloudwatch_logs_exports = var.database_type == "postgres" ? ["postgresql"] : ["error", "general", "slowquery"]

  tags = {
    Name = "${var.platform_name}-${var.database_name}"
  }
}

output "endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
}

output "address" {
  description = "RDS address"
  value       = aws_db_instance.main.address
}

output "port" {
  description = "RDS port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}
