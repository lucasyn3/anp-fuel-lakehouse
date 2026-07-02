# Os grupos anp_engineerss, anp_analystss e anp_adminss sao grupos de conta
# (account-level), provisionados fora do Terraform via Identity and access.
# O recurso databricks_group cria um grupo de conta apenas quando o provider
# aponta para o host de contas (accounts.cloud.databricks.com); com o provider
# workspace-level utilizado neste projeto, ele criaria um grupo workspace-local,
# que nao e um principal valido para GRANT no Unity Catalog. Por isso os grupos
# sao referenciados aqui apenas pelo nome, como strings.

resource "databricks_grants" "anp_lakehouse" {
  catalog = databricks_catalog.anp_lakehouse.name

  grant {
    principal  = "anp_engineerss"
    privileges = ["USE_CATALOG"]
  }

  grant {
    principal  = "anp_analystss"
    privileges = ["USE_CATALOG"]
  }
}

resource "databricks_grants" "bronze" {
  schema = "${databricks_catalog.anp_lakehouse.name}.${databricks_schema.bronze.name}"

  grant {
    principal = "anp_engineerss"
    privileges = [
      "USE_SCHEMA",
      "CREATE_TABLE",
      "CREATE_VOLUME",
      "MODIFY",
      "SELECT",
      "READ_VOLUME",
      "WRITE_VOLUME",
    ]
  }
}

resource "databricks_grants" "silver" {
  schema = "${databricks_catalog.anp_lakehouse.name}.${databricks_schema.silver.name}"

  grant {
    principal  = "anp_engineerss"
    privileges = ["USE_SCHEMA", "CREATE_TABLE", "MODIFY", "SELECT"]
  }
}

resource "databricks_grants" "gold" {
  schema = "${databricks_catalog.anp_lakehouse.name}.${databricks_schema.gold.name}"

  grant {
    principal  = "anp_engineerss"
    privileges = ["USE_SCHEMA", "CREATE_TABLE", "MODIFY", "SELECT"]
  }

  grant {
    principal  = "anp_analystss"
    privileges = ["USE_SCHEMA", "SELECT"]
  }
}
