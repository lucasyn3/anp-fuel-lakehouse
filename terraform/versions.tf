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
  # Autenticacao resolvida automaticamente: variavel DATABRICKS_TOKEN (PAT
  # pessoal) no CI, perfil DEFAULT do ~/.databrickscfg localmente. Service
  # principal (anp-ci) criado mas nao usado: OAuth M2M falhou consistentemente
  # no Free Edition (SCIM, grants e token endpoint nao reconhecem o principal
  # apesar de aparecer ativo na UI — provavel bug da plataforma).
}
