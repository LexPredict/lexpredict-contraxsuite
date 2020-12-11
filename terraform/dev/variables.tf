variable "appId" {
  description = "Azure Kubernetes Service Cluster service principal"
}

variable "password" {
  description = "Azure Kubernetes Service Cluster password"
}

variable "environment" {
  default = "dev"
} 

variable "resource_group_name" {
  default = "default-contraxuite-cluster-rg"
}
variable "aks_dns_prefix" {
  default = "contraxuite-dns-prefix"
}

variable "region" {
  default  = "East US 2"

}

variable "nfs_server_setting_file"{
    type = string
    default = "nfs-server-setup.sh"
}

variable "rook_ceph_os_disk_size_gb" {
  default = 50
}

variable "master_nodepool_node_count" {
  default = 1
}

variable "master_node_pool_vm_size" {
  default = "Standard_DS2_v2"
}

variable "worker_nodepool_node_count_min" {
  default = 1
}

variable "worker_nodepool_node_count_max" {
  default = 30
}

variable "worker_node_pool_vm_size" {
  default = "Standard_DS2_v2"
}

# database.tf

variable "postgresql_service_name" {
  default = "dev-contraxsuite-postgresql-server-1"
}

variable "db_storage_mb" {
  default = 5120
}

variable "db_backup_retention_days"  {
  default = 14
}

variable "db_administrator_login" {
  default = "psqladminun"
}

variable "db_administrator_login_password" {
  default = "asd123Ass&*"
}

variable "azurerm_postgresql_database_name" {
  default = "contrax"
}