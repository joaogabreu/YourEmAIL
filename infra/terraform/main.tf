locals {
  ssh_public_key = file(abspath("${path.module}/../../.infra/youremail-key.pub"))
}

module "storage" {
  source = "./modules/storage"

  project_name          = var.project_name
  environment           = var.environment
  state_bucket_name     = var.state_bucket_name
  artifacts_bucket_name = var.artifacts_bucket_name
}

module "compute" {
  source = "./modules/compute"

  project_name           = var.project_name
  environment            = var.environment
  aws_region             = var.aws_region
  vpc_cidr               = var.vpc_cidr
  instance_type_ec2      = var.instance_type_ec2
  instance_type_ci       = var.instance_type_ci
  ssh_public_key         = local.ssh_public_key
  allowed_ssh_cidr       = var.allowed_ssh_cidr
  eks_node_instance_type = var.eks_node_instance_type
  eks_node_desired_size  = var.eks_node_desired_size
  eks_node_min_size      = var.eks_node_min_size
  eks_node_max_size      = var.eks_node_max_size
}

module "database" {
  source = "./modules/database"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.compute.vpc_id
  private_subnet_ids    = module.compute.private_subnet_ids
  db_username           = var.db_username
  db_password           = var.db_password
  db_name               = var.db_name
  api1_security_group_id = module.compute.api1_security_group_id
  eks_cluster_security_group_id = module.compute.eks_cluster_security_group_id
  ci_security_group_id  = module.compute.ci_security_group_id
  create_read_replica   = var.create_read_replica
}
