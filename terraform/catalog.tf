# Catalog, schemas e volume ja existem (criados manualmente via CLI/UI antes do
# Terraform entrar no projeto). Os blocos abaixo declaram o estado atual para
# `terraform import` os adotar, nao para cria-los do zero.

resource "databricks_catalog" "anp_lakehouse" {
  name         = "anp_lakehouse"
  comment      = "Lakehouse de precos de combustiveis ANP"
  owner        = "anp_adminss"
  storage_root = "s3://dbstorage-prod-224hl/uc/e5ad2c55-3369-4c72-aa49-10b4517fea18/bf7e1747-1f69-4d2a-8c45-3943bc691ab9"
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
