variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_name" {
  type = string
}

variable "api1_security_group_id" {
  type = string
}

variable "eks_cluster_security_group_id" {
  type = string
}

variable "ci_security_group_id" {
  type = string
}

variable "create_read_replica" {
  type = bool
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet"
  subnet_ids = var.private_subnet_ids
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "rds"
  vpc_id      = var.vpc_id

  ingress {
    description     = "api1"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.api1_security_group_id]
  }

  ingress {
    description     = "eks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_cluster_security_group_id]
  }

  ingress {
    description     = "ci"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ci_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "primary" {
  identifier             = "${var.project_name}-${var.environment}-postgres"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  storage_encrypted      = true
  backup_retention_period = 1
}

resource "aws_db_instance" "replica" {
  count = var.create_read_replica ? 1 : 0

  identifier              = "${var.project_name}-${var.environment}-postgres-replica"
  replicate_source_db     = aws_db_instance.primary.identifier
  instance_class          = "db.t3.micro"
  skip_final_snapshot     = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.rds.id]
}

output "rds_endpoint" {
  value = aws_db_instance.primary.address
}

output "rds_port" {
  value = aws_db_instance.primary.port
}

output "rds_read_endpoint" {
  value = var.create_read_replica ? aws_db_instance.replica[0].address : aws_db_instance.primary.address
}

output "db_security_group_id" {
  value = aws_security_group.rds.id
}
