variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "state_bucket_name" {
  type = string
}

variable "artifacts_bucket_name" {
  type = string
}

resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket = aws_s3_bucket.state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "locks" {
  name         = "${var.project_name}-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket = var.artifacts_bucket_name
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_ecr_repository" "api1" {
  name                 = "${var.project_name}-api-1"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

resource "aws_ecr_repository" "api2" {
  name                 = "${var.project_name}-api-2"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

output "state_bucket_name" {
  value = aws_s3_bucket.state.bucket
}

output "ecr_api1_url" {
  value = aws_ecr_repository.api1.repository_url
}

output "ecr_api2_url" {
  value = aws_ecr_repository.api2.repository_url
}

output "artifacts_bucket_name" {
  value = aws_s3_bucket.artifacts.bucket
}

output "dynamodb_lock_table" {
  value = aws_dynamodb_table.locks.name
}
