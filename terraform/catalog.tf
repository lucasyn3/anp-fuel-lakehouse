# Catalog, schemas e volume ja existem (criados manualmente via CLI/UI antes do
# Terraform entrar no projeto). Os blocos abaixo declaram o estado atual para
# `terraform import` os adotar, nao para cria-los do zero.

resource "databricks_catalog" "anp_lakehouse" {
  name         = "anp_lakehouse"
  comment      = "Lakehouse de precos de combustiveis ANP"
  owner        = "anp_admins"
  storage_root = "s3://dbstorage-prod-3emgr/uc/bfea514e-3191-49eb-9346-c778926d7f58/ef070447-27be-40d2-992c-eaa530fa1773"
}

resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.anp_lakehouse.name
  name         = "bronze"
  comment      = "Dados brutos ingeridos do Volume"
}

resource "databricks_schema" "silver" {
  catalog_name = databricks_catalog.anp_lakehouse.name
  name         = "silver"
  comment      = "Dados limpos e deduplicados"
}

resource "databricks_schema" "gold" {
  catalog_name = databricks_catalog.anp_lakehouse.name
  name         = "gold"
  comment      = "Agregacoes de negocio"
}

resource "databricks_volume" "landing" {
  name         = "landing"
  catalog_name = databricks_catalog.anp_lakehouse.name
  schema_name  = databricks_schema.bronze.name
  volume_type  = "MANAGED"
  comment      = "Landing zone dos CSVs da ANP"
}
