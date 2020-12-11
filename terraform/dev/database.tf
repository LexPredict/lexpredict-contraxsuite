
resource "azurerm_postgresql_server" "database" {
  name                = var.postgresql_service_name
  location            = azurerm_resource_group.default.location
  resource_group_name = azurerm_resource_group.default.name

  sku_name = "B_Gen5_2"

  storage_mb                   = var.db_storage_mb
  backup_retention_days        = var.db_backup_retention_days
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = var.db_administrator_login
  administrator_login_password = var.db_administrator_login_password
  version                      = "11"
  ssl_enforcement_enabled      = true
}

resource "azurerm_postgresql_database" "database" {
  name                = var.azurerm_postgresql_database_name
  resource_group_name = azurerm_postgresql_server.database.resource_group_name
  server_name         = azurerm_postgresql_server.database.name
  charset             = "UTF8"
  collation           = "English_United States.1252"
}

resource "azurerm_postgresql_firewall_rule" "database" {
  name                = "k8sClusterAccess"
  resource_group_name = azurerm_postgresql_server.database.resource_group_name
  server_name         = azurerm_postgresql_server.database.name
  start_ip_address    = "52.177.84.55" #TODO get from aks-cluster.tf
  end_ip_address      = "52.177.84.55"
}