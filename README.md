# anp-fuel-lakehouse

Lakehouse medallion (Bronze -> Silver -> Gold) sobre a Serie Historica de Precos de
Combustiveis da ANP, construido no Databricks Free Edition (Unity Catalog +
Lakeflow Declarative Pipelines).

## Escopo

- Ingestao incremental dos CSVs da ANP a partir de um Volume do Unity Catalog.
- Camadas Delta com Auto Loader, deduplicacao/MERGE e agregacoes de negocio.
- Infraestrutura como codigo (Terraform) e CI (GitHub Actions).

## Por que medallion

Reprocessamento auditavel (o dado bruto na Bronze nunca e sobrescrito) e
linhagem ponta a ponta no Unity Catalog, do CSV bruto ate a metrica agregada.

## Arquitetura

```mermaid
flowchart LR
    subgraph ext["Fora do Databricks"]
        anp["ANP<br/>CSVs de precos"]
        ci["GitHub Actions<br/>CI/CD"]
    end

    subgraph uc["Unity Catalog - anp_lakehouse"]
        vol[("Volume<br/>bronze.landing")]
        bronze[["Bronze<br/>precos_combustiveis<br/>(streaming table)"]]
        silver_fact[["Silver<br/>precos_combustiveis<br/>(materialized view, fato)"]]
        silver_dim[["Silver<br/>revendas<br/>(streaming table, SCD2, dimensao)"]]
        silver_produtos[["Silver<br/>produtos<br/>(materialized view, dimensao)"]]
        gold[["Gold<br/>precos_medios<br/>(materialized view)"]]
    end

    job["Job anp_pipeline<br/>agendamento semanal"]

    anp -->|"download_anp.py"| vol
    vol -->|"Auto Loader"| bronze
    bronze --> silver_fact
    bronze --> silver_dim
    silver_produtos --> silver_fact
    silver_fact --> gold
    silver_produtos --> gold
    job -.dispara.-> bronze
    ci -.-> |"databricks bundle deploy<br/>(codigo do pipeline)"| bronze
    ci -.-> |"terraform apply<br/>(catalog/schema/volume/grants)"| uc
```

Terraform provisiona a infraestrutura (catalog, schemas, volume, grants);
Databricks Asset Bundle publica o codigo do pipeline; o Job dispara a
execucao semanal. Ver secao Governanca abaixo pra quem tem acesso a cada
schema.

## Modelo de dados (Star Schema)

Fato no centro, duas dimensoes ao redor, cada uma com sua chave:

```mermaid
erDiagram
    direction LR

    revendas ||--o{ precos_combustiveis : "cnpj_revenda"
    produtos ||--o{ precos_combustiveis : "produto_id"

    revendas {
        string cnpj_revenda PK
        string revenda
        string bandeira
        string nome_rua
        string numero_rua
        string bairro
        string cep
        string municipio
        string estado_sigla
        date data_coleta
        timestamp __START_AT
        timestamp __END_AT
    }

    precos_combustiveis {
        string cnpj_revenda FK
        int produto_id FK
        date data_coleta
        decimal valor_venda
        decimal valor_compra
        string unidade_medida
        string regiao_sigla
        string estado_sigla
        string municipio
    }

    produtos {
        int produto_id PK
        string produto_nome
        string categoria
    }
```

- **Fato `precos_combustiveis`**: 1 linha por observacao de preco. Carrega as
  medidas numericas (`valor_venda`, `valor_compra`) e as chaves estrangeiras
  pras duas dimensoes.
- **Dimensao `revendas`** (SCD Type 2 via AUTO CDC): 1 linha por posto, mas
  com **historico** — troca de bandeira ou endereco gera uma versao nova em
  vez de sobrescrever (`__START_AT`/`__END_AT` controlam a validade de cada
  versao, geradas automaticamente pelo AUTO CDC).
- **Dimensao `produtos`**: dominio pequeno e fixo (os produtos de
  combustivel da ANP), por isso e uma tabela estatica em vez de derivada dos
  dados — padrao comum pra dimensoes de baixa cardinalidade.

## Governanca (Unity Catalog)

Catalog `anp_lakehouse`, schemas `bronze`/`silver`/`gold`, volume de landing
`anp_lakehouse.bronze.landing` (destino dos CSVs crus da ANP).

Acesso concedido por grupo a nivel de schema, herdado por toda tabela criada
dentro dele:

| Grupo | Escopo | Privilegios |
|---|---|---|
| `anp_admins` | catalog `anp_lakehouse` | owner |
| `anp_engineers` | schema `bronze` (+ volume `landing`) | USE_SCHEMA, CREATE_TABLE, CREATE_VOLUME, MODIFY, SELECT, READ_VOLUME, WRITE_VOLUME |
| `anp_engineers` | schemas `silver`, `gold` | USE_SCHEMA, CREATE_TABLE, MODIFY, SELECT |
| `anp_analysts` | schema `gold` | USE_SCHEMA, SELECT (somente leitura, perfil dashboard) |

### Column mask (PII)

`cnpj_revenda` em `silver.revendas` tem uma mascara de coluna nativa do
Unity Catalog: quem nao e `anp_engineers`/`anp_admins` ve so os 4 ultimos
digitos, nao o CNPJ completo.

```sql
CREATE OR REPLACE FUNCTION anp_lakehouse.silver.mask_cnpj(cnpj STRING)
RETURN CASE
    WHEN is_account_group_member('anp_engineers') OR is_account_group_member('anp_admins') THEN cnpj
    ELSE CONCAT('**.***.***/****-', right(cnpj, 4))
END;

ALTER TABLE anp_lakehouse.silver.revendas ALTER COLUMN cnpj_revenda SET MASK anp_lakehouse.silver.mask_cnpj;
```

Diferente de uma view que so omite coluna, a mascara fica **na tabela
original**: a coluna continua existindo pra todo mundo, mas o **valor**
retornado muda dependendo de quem consulta — `is_account_group_member()` e
avaliado a cada query. Aplicado direto via SQL (nao esta no Terraform ainda).

## Estrutura do repositorio

- `terraform/` - IaC do catalog, schemas, volume e grants no Unity Catalog.
- `src/` - codigo das camadas Bronze/Silver/Gold do Lakeflow Pipeline.
- `resources/` + `databricks.yml` - Databricks Asset Bundle: deploy do codigo
  do pipeline. O job de agendamento (`anp_job`) e gerenciado manualmente pela
  UI (`resources/disabled/anp_job.job.yml` documenta o motivo).
- `download/` - script de download dos CSVs da ANP.
- `tests/` - testes unitarios do script de download.
- `.github/workflows/` - CI (lint + testes + `terraform validate` sempre;
  deploy no push pra `main`, condicional aos secrets `DATABRICKS_HOST` e
  `DATABRICKS_TOKEN` no repositorio).