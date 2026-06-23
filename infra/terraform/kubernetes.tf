data "aws_eks_cluster" "main" {
  name = module.compute.eks_cluster_name

  depends_on = [module.compute]
}

data "aws_eks_cluster_auth" "main" {
  name = module.compute.eks_cluster_name

  depends_on = [module.compute]
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.main.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.main.token
}

resource "kubernetes_namespace" "youremail" {
  metadata {
    name = "youremail"
    labels = {
      "app.kubernetes.io/name"       = "youremail"
      "app.kubernetes.io/part-of"  = "youremail"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  depends_on = [module.compute]
}
