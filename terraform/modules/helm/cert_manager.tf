resource "helm_release" "cert_manager" {
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
