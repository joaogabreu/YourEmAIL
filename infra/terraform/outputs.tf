output "gateway_private_ip" {
  value = module.compute.gateway_private_ip
}

output "gateway_public_ip" {
  value = module.compute.gateway_public_ip
}

output "gateway_url" {
  value = "http://${module.compute.gateway_public_ip}"
}

output "api1_private_ip" {
  value = module.compute.api1_private_ip
}

output "ci_public_ip" {
  value = module.compute.ci_public_ip
}

output "sonarqube_url" {
  value = "http://${module.compute.ci_public_ip}:9000"
}

output "rds_endpoint" {
  value = module.database.rds_endpoint
}

output "rds_read_endpoint" {
  value = module.database.rds_read_endpoint
}

output "eks_cluster_name" {
  value = module.compute.eks_cluster_name
}

output "eks_cluster_endpoint" {
  value = module.compute.eks_cluster_endpoint
}

output "state_bucket_name" {
  value = module.storage.state_bucket_name
}

output "artifacts_bucket_name" {
  value = module.storage.artifacts_bucket_name
}

output "ecr_api1_url" {
  value = module.storage.ecr_api1_url
}

output "ecr_api2_url" {
  value = module.storage.ecr_api2_url
}

output "public_subnet_ids" {
  value = join(",", module.compute.public_subnet_ids)
}
