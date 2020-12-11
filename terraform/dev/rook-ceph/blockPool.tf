resource "kubernetes_manifest" "cephblockpool_replicapool" {
  provider = kubernetes-alpha
  depends_on = [kubernetes_manifest.cephcluster_rook_ceph]
  manifest = {
    "apiVersion" = "ceph.rook.io/v1"
    "kind" = "CephBlockPool"
    "metadata" = {
      "name" = "replicapool"
      "namespace" = "rook-ceph"
    }
    "spec" = {
      "failureDomain" = "host"
      "replicated" = {
        "size" = 3
      }
    }
  }
}
