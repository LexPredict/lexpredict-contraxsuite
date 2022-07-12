resource "helm_release" "ceph_cluster_dev" {
  count = var.ceph_cluster_environment == "dev" ? 1 : 0
  name = "rook-ceph-cluster"
  chart = "rook-ceph-cluster"
  repository = "https://charts.rook.io/release"
  namespace = "rook-ceph"

  set {
    name  = "operatorNamespace"
    value = "rook-ceph"
  }
  
  values = [
    "${file("${path.module}/helm-dev-values.yaml")}"
  ]
}
resource "helm_release" "ceph_cluster_prd" {
  count = var.ceph_cluster_environment == "prd" ? 1 : 0
  name = "ceph-cluster"
  chart = "${path.module}/ceph_cluster"

  namespace = "rook-ceph"

  set {
    name  = "operatorNamespace"
    value = "rook-ceph"
  }
  
  values = [
    "${file("${path.module}/helm-prd-values.yaml")}"
  ]
}
