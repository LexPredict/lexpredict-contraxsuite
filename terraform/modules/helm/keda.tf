resource "helm_release" "keda" {
  count = var.install_keda ? 1 : 0
  name = "keda"
  repository = "https://kedacore.github.io/charts"
  chart = "keda"
  #version = "1.4.2"
  create_namespace = true
  namespace = "keda"
}