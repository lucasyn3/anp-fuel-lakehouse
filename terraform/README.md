# terraform/

Infraestrutura como codigo para o workspace Databricks (provider `databricks`).

Gerencia: catalog `anp_lakehouse`, schemas (bronze/silver/gold), volume de
landing e os grants por schema (ver README raiz, secao Governanca). Todos
adotados via `terraform import` a partir de recursos que ja existiam, criados
manualmente durante o desenvolvimento inicial do projeto.

Fora do escopo do Terraform, por decisao de arquitetura:
- **Grupos de conta** (`anp_engineerss`, `anp_analystss`, `anp_adminss`):
  provisionados via Identity and access. Ver comentario em `grants.tf`.
- **Pipeline, job e codigo de transformacao**: gerenciados via Databricks
  Asset Bundle (`databricks.yml` + `resources/*.yml` na raiz do repo), nao
  pelo Terraform.
- **SQL warehouse**: ainda nao criado (Fase 7 do plano).

## Autenticacao

O provider nao fixa metodo de autenticacao, por isso funciona tanto local
quanto no CI:

- Local: `export DATABRICKS_CONFIG_PROFILE=DEFAULT` (usa o `~/.databrickscfg`
  ja configurado pelo Databricks CLI).
- CI: variaveis `DATABRICKS_HOST` e `DATABRICKS_TOKEN` (secrets do GitHub
  Actions).
