
provider "azurerm" {
  features {}
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

#provider "kubernetes-alpha" {
#  config_path = "~/.kube/config"
#}

resource "azurerm_resource_group" "default" {
  name     = var.resource_group_name
  location = var.location
  tags = {
    environment = var.environment
  }
}

module "vnet" {
  source              = "Azure/vnet/azurerm"
  version             = "2.6.0"
  resource_group_name = azurerm_resource_group.default.name
  address_space       = ["172.16.0.0/16"]
  subnet_prefixes     = ["172.16.1.0/24"]
  subnet_names        = ["subnet1"]

  subnet_service_endpoints = {
    subnet1 = ["Microsoft.Sql"],
  }

  tags = {
    environment = var.environment,
  }

  depends_on = [azurerm_resource_group.default]
}

module "aks_cluster" {
  source     = "../modules/azure/aks-cluster"
  depends_on = [azurerm_resource_group.default, module.vnet]
  # Global Settings
  appId               = var.appId
  password            = var.password
  environment         = var.environment
  vnet_subnet_id      = module.vnet.vnet_subnets[0]
  aks_dns_prefix      = var.aks_dns_prefix
  kubernetes_version  = var.k8s_version
  resource_group_name = azurerm_resource_group.default.name
  location            = azurerm_resource_group.default.location
  # Master Node Pool
  master_node_count = var.master_nodepool_count
  master_vm_size    = var.master_nodepool_vm_size
  # Worker Node Pool
  worker_vm_size   = var.worker_nodepool_vm_size
  worker_min_count = var.worker_nodepool_count_min
  worker_max_count = var.worker_nodepool_count_max
  worker_priority  = var.worker_nodepool_priority
  # Rook Ceph Node Pool
  rook_ceph_os_disk_size_gb = var.rook_ceph_nodepool_os_disk_size_gb
  rook_ceph_priority        = var.rook_ceph_nodepool_priority
  rook_ceph_node_count      = var.rook_ceph_nodepool_count
  rook_ceph_vm_size         = var.rook_ceph_nodepool_vm_size
}

module "postgresql" {
  count      = var.db_module_enable ? 1 : 0
  source     = "Azure/postgresql/azurerm"
  version    = "2.1.0"
  depends_on = [azurerm_resource_group.default, module.vnet]
  # Settings
  resource_group_name          = azurerm_resource_group.default.name
  location                     = azurerm_resource_group.default.location
  server_name                  = var.db_server_name
  sku_name                     = var.db_sku_name
  storage_mb                   = var.db_storage_mb
  backup_retention_days        = var.db_backup_retention_days
  geo_redundant_backup_enabled = false
  administrator_login          = var.db_administrator_login
  administrator_password       = var.db_administrator_login_password
  server_version               = "11"
  ssl_enforcement_enabled      = false
  db_names                     = [var.db_name]
  db_charset                   = "UTF8"
  db_collation                 = "English_United States.1252"
  #firewall_rule_prefix         = "firewall-"
  #firewall_rules               = [
  #  { start_ip = "20.41.41.162", end_ip = "20.41.41.162" }, #TODO Add public IPs of default node poll VMs
  #]

  vnet_rule_name_prefix = "db-vnet-rule-"
  vnet_rules = [
    { name = "subnet1", subnet_id = module.vnet.vnet_subnets[0] }
  ]

  tags = {
    environment = var.environment,
  }

  postgresql_configurations = {
    backslash_quote = "on",
  }
}
# Install additional k8s resources required for app
module "helm_charts" {
  source                = "../modules/helm"
  resource_group_name   = azurerm_resource_group.default.name
  install_cert_manager  = var.helm_install_cert_manager
  install_ingress_nginx = var.helm_install_ingress
  install_keda          = var.helm_install_keda
  install_monitoring    = var.helm_install_monitoring
  grafana_domain        = var.main_domain
  install_rook_ceph     = var.helm_install_rook_ceph
  # Ceph Cluster Section
  # NOTE ceph_cluster_deploy should be false until rook ceph succesfully installed 
  ceph_cluster_environment = var.ceph_cluster_environment
  rook_version             = var.ceph_cluster_rook_version
  ceph_version             = var.ceph_cluster_ceph_version
  #depends_on = [module.aks_cluster]
}