resource "helm_release" "cert-manager" {
  count = var.install_cert_manager ? 1 : 0
  name = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart = "cert-manager"
  
  create_namespace = true
  namespace = "cert-manager"

  set {
    name = "installCRDs"
    value = "true"
  }
} 
resource "helm_release" "ingress" {
    count = var.install_ingress ? 1 : 0
    name      = "ingress"
    repository = "https://kubernetes.github.io/ingress-nginx"
    chart     = "ingress-nginx"
    timeout   = 600

    create_namespace = true
    namespace = "ingress"

    set {
        name  = "rbac.create"
        value = "true"
    }

    set {
      name  = "controller.service.externalTrafficPolicy"
      value = "Local"
    }
  
    set {
      name = "service.beta.kubernetes.io/azure-load-balancer-resource-group"
      value = var.resource_group_name
    }

    set {
        name  = "metrics.enabled"
        value = "false"
  }
}

resource "helm_release" "monitoring" {
    count = var.install_monitoring ? 1 : 0
    repository = "https://prometheus-community.github.io/helm-charts"
    name       = "monitoring"
    chart      = "kube-prometheus-stack"
    timeout    = 600
    create_namespace = true
    namespace = "monitoring"
    values = [
    file(var.monitoring_values_file)
  ]
}

resource "helm_release" "rook-ceph" {
  count = var.install_rook_ceph ? 1 : 0
  lifecycle {
    ignore_changes = all # Run only once
  }
  name = "rook-ceph"
  repository = "https://charts.rook.io/release"
  chart = "rook-ceph"

  create_namespace = true
  namespace = "rook-ceph"

  values = [
    file(var.rook_ceph_values_file)
  ]
}

resource "helm_release" "keda" {
  count = var.install_keda ? 1 : 0
  name = "keda"
  repository = "https://kedacore.github.io/charts"
  chart = "keda"
  #version = "1.4.2"
  create_namespace = true
  namespace = "keda"
}