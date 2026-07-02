# terraform/

Infraestrutura como codigo para o workspace Databricks (provider `databricks`)

Recursos previstos: catalog, schemas (bronze/silver/gold), volume, grupos e
grants, Lakeflow Declarative Pipeline, job e SQL warehouse.

Catalog, schemas, volume, grupos e grants ja existem, criados manualmente via
CLI/UI (ver README raiz, secao Governanca). Ao escrever esses recursos aqui,
usar `terraform import` em vez de recriar.
