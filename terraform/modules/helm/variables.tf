variable "resource_group_name" {
  default = "ingress_resource_group_name"
  type = string
}
variable "install_cert_manager" {
  default = false
  type = string
  description = "Should Cert Manager Helm Chart be installed"
}
variable "install_ingress" {
  default = false
  type = string
  description = "Should Ingress-Nginx Helm Chart be installed"
}
variable "install_monitoring" {
  default = false
  type = string
  description = "Should Kube-prometheus-stack Helm Chart be installed"
}
variable "install_rook_ceph" {
  default = false
  type = string
  description = "Should Rook Ceph Helm Chart be installed"
}
variable "rook_ceph_values_file" {
  default = "rook-ceph-values.yaml"
  type = string
  description = "Path to Rook Ceph Helm Chart config"
}
variable "monitoring_values_file" {
  default = "monitoring-values.yaml"
  description = "Path to Kube-Prometheus-Stack Helm Chart config"
}
variable "install_keda" {
  default = false
  type = string
  description = "Should Keda Helm Chart be installed"
}