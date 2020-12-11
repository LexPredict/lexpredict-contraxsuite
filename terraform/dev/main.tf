provider "azurerm" {
  version = "=2.20.0"
  features {}
}

resource "azurerm_resource_group" "default" {
  name     = var.resource_group_name
  location = var.region

  tags = {
    environment = var.environment
  }
}
