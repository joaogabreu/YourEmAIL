variable "project_name" {
  type    = string
  default = "youremail"
}

variable "environment" {
  type    = string
  default = "homolog"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
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
  type    = string
  default = "youremail"
}

variable "instance_type_ec2" {
  type    = string
  default = "t3.micro"
}

variable "instance_type_ci" {
  type    = string
  default = "t3.micro"
}

variable "eks_node_instance_type" {
  type    = string
  default = "t3.micro"
}

variable "eks_node_desired_size" {
  type    = number
  default = 2
}

variable "eks_node_min_size" {
  type    = number
  default = 2
}

variable "eks_node_max_size" {
  type    = number
  default = 4
}

variable "allowed_ssh_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

variable "create_read_replica" {
  type    = bool
  default = true
}

variable "state_bucket_name" {
  type    = string
  default = "youremail-tfstate-253440504787"
}

variable "artifacts_bucket_name" {
  type    = string
  default = "youremail-artifacts-253440504787"
}
