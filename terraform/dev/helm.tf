
provider "helm" {
  version = "1.2.2"
  kubernetes {
    host = azurerm_kubernetes_cluster.cluster.kube_config[0].host

    client_key             = base64decode(azurerm_kubernetes_cluster.cluster.kube_config[0].client_key)
    client_certificate     = base64decode(azurerm_kubernetes_cluster.cluster.kube_config[0].client_certificate)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.cluster.kube_config[0].cluster_ca_certificate)
    load_config_file       = false
  }
}


resource "helm_release" "ingress" {
    name      = "ingress"
    chart     = "stable/nginx-ingress"
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
    value = "${azurerm_resource_group.default.name}"
  }

    set {
        name  = "metrics.enabled"
        value = "false"
  }
}

resource "helm_release" "monitoring" {
    name      = "monitoring"
    chart     = "stable/prometheus-operator"
    timeout   = 600

    create_namespace = true
    namespace = "monitoring"
}

resource "helm_release" "cert-manager" {
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

resource "helm_release" "rook-ceph" {
  name = "rook-ceph"
  repository = "https://charts.rook.io/release"
  chart = "rook-ceph"

  create_namespace = true
  namespace = "rook-ceph"

  values = [
    "${file("rook-ceph-values.yaml")}"
  ]
}