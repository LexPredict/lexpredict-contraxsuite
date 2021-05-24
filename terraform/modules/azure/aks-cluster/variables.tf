variable "appId" {
  description = "Azure Kubernetes Service Cluster service principal"
  type = string
  default = null
}

variable "password" {
  description = "Azure Kubernetes Service Cluster password"
  type = string
  default = null
}
variable "kubernetes_version" {
  description = "k8s verion to use"
  default = "1.18.14"
}
variable "environment" {
  default = "dev"
  description = "Environment for tags"
  type = string
} 
variable "location" {
  description = "Azure Region"
  default  = "East US 2"
  type = string
}
variable "resource_group_name" {
  default = "default-contraxuite-cluster-rg"
  description = "Azure Resource"
  type = string
}
variable "aks_dns_prefix" {
  description = "AKS dns prefix"
  default = "contraxuite-dns-prefix"
  type = string
}
variable "vnet_subnet_id" {
  type        = string
  default     = null
}
variable "master_node_count" {
  type = string
  default = 2
}
variable "master_vm_size" {
  default = "Standard_F8s_v2"
  type = string
}
variable "worker_priority" {
  default= "Regular"
  type = string
}
variable "worker_min_count" {
  default = 1
  type = string
}
variable "worker_max_count" {
  default = 30
  type = string
}
variable "worker_vm_size" {
  default = "Standard_D4s_v4"
  type = string
}
# --- Rook Ceph Setting--- # 
variable "rook_ceph_priority" {
  default= "Regular"
  type = string
}
variable "rook_ceph_os_disk_size_gb" {
  default = 50
  type = string
}
variable "rook_ceph_node_count" {
  default = 3
  type = string
}
variable "rook_ceph_vm_size" {
  type = string
  default = "Standard_DS2_v2"
}
