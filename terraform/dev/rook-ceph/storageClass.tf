resource "kubernetes_manifest" "storageclass_rook_ceph_block" {
  depends_on = [kubernetes_manifest.cephblockpool_replicapool]
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "storage.k8s.io/v1"
    "kind" = "StorageClass"
    "metadata" = {
      "name" = "rook-ceph-block"
    }
    "parameters" = {
      "clusterID" = "rook-ceph"
      "csi.storage.k8s.io/fstype" = "xfs"
      "csi.storage.k8s.io/node-stage-secret-name" = "rook-csi-rbd-node"
      "csi.storage.k8s.io/node-stage-secret-namespace" = "rook-ceph"
      "csi.storage.k8s.io/provisioner-secret-name" = "rook-csi-rbd-provisioner"
      "csi.storage.k8s.io/provisioner-secret-namespace" = "rook-ceph"
      "imageFeatures" = "layering"
      "imageFormat" = "2"
      "pool" = "replicapool"
    }
    "provisioner" = "rook-ceph.rbd.csi.ceph.com"
    "reclaimPolicy" = "Delete"
  }
}
