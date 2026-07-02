# anp-fuel-lakehouse

Lakehouse medallion (Bronze -> Silver -> Gold) sobre a Serie Historica de Precos de
Combustiveis da ANP, construido no Databricks Free Edition (Unity Catalog +
Lakeflow Declarative Pipelines).

## Escopo

- Ingestao incremental dos CSVs da ANP a partir de um Volume do Unity Catalog.
- Camadas Delta com Auto Loader, deduplicacao/MERGE e agregacoes de negocio.
- Infraestrutura como codigo (Terraform) e CI (GitHub Actions), quando um
  Personal Access Token do workspace estiver disponivel.
- Dashboard AI/BI sobre a camada Gold.

## Por que medallion

Reprocessamento auditavel (o dado bruto na Bronze nunca e sobrescrito) e
linhagem ponta a ponta no Unity Catalog, do CSV bruto ate a metrica agregada.

## Estrutura do repositorio

- `terraform/` - IaC do workspace Databricks (condicional a PAT).
- `src/` - codigo das camadas Bronze/Silver/Gold e do Lakeflow Pipeline.
- `download/` - script de download dos CSVs da ANP.
- `tests/` - testes unitarios das transformacoes.
- `.github/workflows/` - CI (validacao sempre; deploy condicional a PAT).