resource "helm_release" "rook_ceph" {
  count = var.install_rook_ceph ? 1 : 0
  name = "rook-ceph"
  repository = "https://charts.rook.io/release"
  chart = "rook-ceph"

  create_namespace = true
  namespace = "rook-ceph"

  set {
    name  = "image.tag"
    value = var.rook_version
  }
  set {
    name = "nodeSelector.agentpool"
    value = "rookceph"
  }
  set {
    name = "tolerations[0].key"
    value = "storage-node"
  }
  set {
    name = "tolerations[0].operator"
    value = "Exists"
  }
  set {
    name = "tolerations[0].effect"
    value = "NoSchedule"
  }
}