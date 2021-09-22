resource "helm_release" "ceph_cluster" {
  count = var.ceph_cluster_deploy ? 1 : 0
  name = "ceph-cluster"
  chart = "${path.module}/ceph_cluster"

  namespace = "rook-ceph"

  set {
    name  = "cephVersion"
    value = var.ceph_version
  }
  set {
    name = "rookVersion" 
    value = var.rook_version
  }
}