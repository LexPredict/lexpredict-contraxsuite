resource "null_resource" "ceph_cluster" {
  count = var.deploy_ceph_cluster ? 1 : 0
  provisioner "local-exec" {
    command = "kubectl apply -f ${path.module}/ceph_cluster.yaml"
  }
}

resource "null_resource" "ceph_block_pool" {
  count = var.deploy_ceph_cluster ? 1 : 0
  provisioner "local-exec" {
    command = "kubectl apply -f ${path.module}/ceph_block_pool.yaml"
  }
}

resource "null_resource" "storage_class" {
  count = var.deploy_ceph_cluster ? 1 : 0
  provisioner "local-exec" {
    command = "kubectl apply -f ${path.module}/storage_class.yaml"
  }
}

resource "null_resource" "rook_toolbox" {
  count = var.deploy_ceph_cluster ? 1 : 0
  provisioner "local-exec" {
    command = "kubectl apply -f ${path.module}/rook_toolbox.yaml"
  }
}