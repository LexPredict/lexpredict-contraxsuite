resource "helm_release" "ingress_nginx" {
    count = var.install_ingress_nginx ? 1 : 0
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
