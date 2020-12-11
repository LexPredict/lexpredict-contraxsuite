
resource "azurerm_kubernetes_cluster" "cluster" {
  name                = "${var.aks_dns_prefix}-aks"
  location            = azurerm_resource_group.default.location
  resource_group_name = azurerm_resource_group.default.name
  kubernetes_version  = "1.18.8"
  dns_prefix          = var.aks_dns_prefix

  network_profile {
    network_plugin      = "kubenet"
    load_balancer_sku   = "Standard" 
  }
  
  default_node_pool {
    name            = "master"
    node_count      = var.master_nodepool_node_count
    vm_size         = var.master_node_pool_vm_size
    vnet_subnet_id  = azurerm_subnet.internal.id
    node_labels = {
      "role" = "manager"
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
  kubernetes_cluster_id = azurerm_kubernetes_cluster.cluster.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 3
  node_taints           = ["storage-node=true:NoSchedule"]
  os_disk_size_gb       = var.rook_ceph_os_disk_size_gb
  vnet_subnet_id        = azurerm_subnet.internal.id

  tags = {
    environment = var.environment
  }
}


resource "azurerm_kubernetes_cluster_node_pool" "worker" {
  name                  = "worker"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.cluster.id
  vm_size               = var.worker_node_pool_vm_size
  enable_auto_scaling = true 
  max_count           = var.worker_nodepool_node_count_max
  min_count           = var.worker_nodepool_node_count_min
  vnet_subnet_id      = azurerm_subnet.internal.id
  node_labels = {
    "role" = "worker"
  }

  tags = {
    environment = var.environment
  }
}

# data "azurerm_public_ip" "cluster" {
#   name                = reverse(split("/", tolist(azurerm_kubernetes_cluster.cluster.network_profile.0.load_balancer_profile.0.effective_outbound_ips)[0]))[0]
#   resource_group_name = azurerm_resource_group.default.name
# }

# output "cluster_egress_ip" {
#   value = data.azurerm_public_ip.cluster.ip_address
# }