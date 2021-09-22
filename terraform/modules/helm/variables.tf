# --- Cert-Manager --- #
variable "install_cert_manager" {
  default = false
  type = string
  description = "Should Cert Manager Helm Chart be installed"
}
# --- Ingress Nginx --- #
variable "install_ingress_nginx" {
  default = false
  type = string
  description = "Should Ingress-Nginx Helm Chart be installed"
}
variable "resource_group_name" {
  default = "ingress_resource_group_name"
  type = string
}
# --- Keda --- # 
variable "install_keda" {
  default = false
  type = string
  description = "Should Keda Helm Chart be installed"
}

# --- Kube Prometheus Stack --- # 
variable "install_monitoring" {
  default = false
  type = string
  description = "Should Kube-prometheus-stack Helm Chart be installed"
}

variable "grafana_domain" {
  default = "_"
  type = string
  description = "Application domain"
}
# --- Rook Ceph --- # 
variable "install_rook_ceph" {
  default = false
  type = string
  description = "Should Rook Ceph Helm Chart be installed"
}
variable "ceph_cluster_deploy" {
  default = false
  type = string
  description = "Setup Ceph Cluster"
}
variable "rook_version" {
  default = "v1.6.7"
  type = string
  description = "Version of rook/ceph image to deploy"
}
variable "ceph_version" {
  default = "v15.2.13"
  type = string
  description = "Version of ceph/ceph image to deploy"
}

#variable "rook_ceph_values_file" {
#  default = "rook-ceph-values.yaml"
#  type = string
#  description = "Path to Rook Ceph Helm Chart config"
#}
#variable "monitoring_values_file" {
#  default = "monitoring-values.yaml"
#  description = "Path to Kube-Prometheus-Stack Helm Chart config"
#}
