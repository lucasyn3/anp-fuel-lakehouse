terraform {
  required_version = ">= 1.5"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.107"
    }
  }
}

provider "databricks" {
  host = var.databricks_host
  # Autenticacao resolvida automaticamente: variaveis DATABRICKS_TOKEN/HOST no
  # CI, perfil DEFAULT do ~/.databrickscfg localmente.
}
