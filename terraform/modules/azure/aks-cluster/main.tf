data "azurerm_resource_group" "default" {
  name = var.resource_group_name
}

resource "azurerm_kubernetes_cluster" "cluster" {
  name                = "${var.aks_dns_prefix}-aks"
  location            = var.location
  resource_group_name = data.azurerm_resource_group.default.name
  kubernetes_version  = var.kubernetes_version
  dns_prefix          = var.aks_dns_prefix

  network_profile {
    network_plugin    = "kubenet"
    load_balancer_sku = "Standard"
  }

  default_node_pool {
    name           = "default"
    node_count     = var.master_node_count
    vm_size        = var.master_vm_size
    vnet_subnet_id = var.vnet_subnet_id
    node_labels = {
      "contraxsuite.com/role" = "manager"
    }

  }

  service_principal {
    client_id     = var.appId
    client_secret = var.password
  }

  role_based_access_control {
    enabled = true
  }

  tags = {
    environment = var.environment
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "rookceph" {
  name                  = "rookceph"
  priority              = var.rook_ceph_priority
  kubernetes_cluster_id = azurerm_kubernetes_cluster.cluster.id
  vm_size               = var.rook_ceph_vm_size
  node_count            = var.rook_ceph_node_count
  os_disk_size_gb = var.rook_ceph_os_disk_size_gb
  vnet_subnet_id  = var.vnet_subnet_id
  node_labels = {
    "contraxsuite.com/role" = "storage-node"
  }
  node_taints = [
    "storage-node=true:NoSchedule",
  ]
  tags = {
    environment = var.environment
  }
}
resource "azurerm_kubernetes_cluster_node_pool" "worker" {
  name                  = "worker"
  priority              = var.worker_priority
  kubernetes_cluster_id = azurerm_kubernetes_cluster.cluster.id
  vm_size               = var.worker_vm_size
  enable_auto_scaling   = true
  max_count             = var.worker_max_count
  min_count             = var.worker_min_count
  vnet_subnet_id        = var.vnet_subnet_id
  eviction_policy       = "Delete"
  node_labels = {
    "contraxsuite.com/role" = "worker",
    "kubernetes.azure.com/scalesetpriority" = "spot",
  }
  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
  ]

  tags = {
    environment = var.environment
  }
}