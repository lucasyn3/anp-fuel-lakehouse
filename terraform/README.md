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

O provider nao fixa metodo de autenticacao. Local:
`export DATABRICKS_CONFIG_PROFILE=DEFAULT` (usa o `~/.databrickscfg` ja
configurado pelo Databricks CLI).

## Estado e por que `apply` nao roda no CI

O `terraform.tfstate` e local (backend padrao) e esta no `.gitignore` — nao e
versionado. O job de CI faz `terraform init -backend=false` e `terraform
validate` (checagem de sintaxe, sem credenciais, sem tocar na infraestrutura
real), mas nao roda `apply`: sem o state persistido, cada execucao do CI
partiria do zero e tentaria recriar os 9 recursos que ja existem, o que falha
(e, em outro provider, poderia tentar duplicar recursos). Ate ter um backend
remoto configurado, `apply` e sempre manual, local, com o state que ja existe
na maquina de quem esta rodando.
