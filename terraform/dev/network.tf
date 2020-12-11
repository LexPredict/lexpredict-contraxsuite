resource "azurerm_virtual_network" "default" {
  name                = "${azurerm_resource_group.default.name}-vnet"
  address_space       = ["172.16.0.0/16"]
  location            = azurerm_resource_group.default.location
  resource_group_name = azurerm_resource_group.default.name
}

resource "azurerm_subnet" "internal" {
  name                 = "private_interface"
  resource_group_name  = azurerm_resource_group.default.name
  virtual_network_name = azurerm_virtual_network.default.name
  address_prefix       = "172.16.2.0/24"
}


resource "azurerm_network_interface" "default" {
  name                = "${azurerm_resource_group.default.name}-nic"
  location            = var.region
  resource_group_name = azurerm_resource_group.default.name

  ip_configuration {
    name                          = "dev-iface-config"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}
