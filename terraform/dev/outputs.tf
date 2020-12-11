output "aks_host" {
  value = azurerm_kubernetes_cluster.cluster.kube_config[0].host
}

# output "cluster_egress_ip" {
#   value = data.azurerm_public_ip.cluster.ip_address
# }