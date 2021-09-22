### --- Permissions Section --- ###
variable "appId" {
  description = "Azure Kubernetes Service Cluster service principal"
  type        = string
}

variable "password" {
  description = "Azure Kubernetes Service Cluster password"
  type        = string
}

### --- Enviromnent Section --- ###
variable "environment" {
  default = "dev"
  type    = string
}

variable "location" {
  default = "East US 2"
  type    = string
}
variable "main_domain" {
  default     = "_"
  type        = string
  description = "Root Domain name used for application"
}
variable "resource_group_name" {
  default = "default-contraxuite-cluster-rg"
  type    = string
}
variable "aks_dns_prefix" {
  default = "contraxuite-dns-prefix"
  type    = string
}

variable "nfs_server_setting_file" {
  type    = string
  default = "nfs-server-setup.sh"
}

### ---- Cluser Node Pools --- ###
# Default Pool
variable "master_nodepool_count" {
  default = 1
  type    = string
}

variable "master_nodepool_vm_size" {
  default = "Standard_D8_v3"
  type    = string
}

# Temp Worker Pool
variable "worker_nodepool_count_min" {
  default = 1
  type    = string
}

variable "worker_nodepool_count_max" {
  default = 10
  type    = string
}

variable "worker_nodepool_vm_size" {
  default = "Standard_D8_v3"
  type    = string
}

variable "worker_nodepool_priority" {
  default = "Regular"
  type    = string
}

# Ceph Cluster Pool
variable "rook_ceph_nodepool_priority" {
  default = "Regular"
  type    = string
}
variable "rook_ceph_nodepool_os_disk_size_gb" {
  default = 250
  type    = string
}
variable "rook_ceph_nodepool_vm_size" {
  default = "Standard_D8_v3"
  type    = string
}
variable "rook_ceph_nodepool_count" {
  default = 3
  type    = string
}
### --- Managed Database Section --- #

variable "db_sku_name" {
  description = "Specifies the SKU Name for this PostgreSQL Server. The name of the SKU, follows the tier + family + cores pattern (e.g. B_Gen4_1, GP_Gen5_8)."
  default     = "GP_Gen5_4"
  type        = string
}

variable "db_module_enable" {
  default = true
  type    = string
}

variable "db_server_name" {
  default = "dev-contraxsuite-postgresql-server-1"
  type    = string
}

variable "db_storage_mb" {
  default = 262144
  type    = string
}

variable "db_backup_retention_days" {
  default = 7
  type    = string
}

variable "db_administrator_login" {
  default = "psqladminun"
  type    = string
}

variable "db_administrator_login_password" {
  default = "asd123Ass&*"
  type    = string
}

variable "db_name" {
  default = "contrax"
  type    = string
}

# kube alpha
variable "kubeconfig" {
  default = "~/.kube/config"
  type    = string
}

variable "k8s_version" {
  default = "1.19.11"
  type    = string
}
# Helm Charts
variable "helm_install_cert_manager" {
  default     = false
  type        = string
  description = "Should Cert Manager Helm Chart be installed"
}
variable "helm_install_ingress" {
  default     = false
  type        = string
  description = "Should Ingress-Nginx Helm Chart be installed"
}
variable "helm_install_monitoring" {
  default     = false
  type        = string
  description = "Should Kube-prometheus-stack Helm Chart be installed"
}
variable "helm_install_rook_ceph" {
  default     = false
  type        = string
  description = "Should Rook Ceph Helm Chart be installed"
}

variable "helm_install_keda" {
  default     = false
  type        = string
  description = "Should Keda Helm Chart be installed"
}
variable "ceph_cluster_deploy" {
  default     = false
  type        = string
  description = ""
}
variable "ceph_cluster_rook_version" {
  default     = "v1.5.11"
  type        = string
  description = ""
}
variable "ceph_cluster_ceph_version" {
  default     = "v15.2.11"
  type        = string
  description = ""
}
