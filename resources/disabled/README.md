# resources/disabled/

Recursos de bundle escritos mas fora do deploy ativo (o `databricks.yml`
inclui so `resources/*.yml`, essa pasta nao entra no glob).

- `anp_job.job.yml`: falha em `databricks bundle deploy` com "Organization
  ... has been cancelled or is not active yet" (403) ao criar o Job, mesmo
  com o pipeline e o resto do bundle funcionando. Sem Account Console no
  Free Edition pra diagnosticar a causa.

  O bloqueio e especifico da API `POST /api/2.2/jobs/create` usada pelo
  bundle/CLI: criar o mesmo job pela UI (Jobs & Pipelines -> abre o
  `anp_pipeline` -> botao **Schedule** -> Weekly) funcionou sem erro em
  ambas as contas. O job existe hoje gerenciado manualmente pela UI, com
  agendamento semanal - nao pelo bundle. Na conta definitiva (`free2`), o
  job se chama **`anp_pipeline`** (nome que a UI preencheu por padrao, nao
  `anp_job`), roda toda sexta-feira 00:53 America/Sao_Paulo, job_id
  `902849683188471`. Mover esse yml de volta pra `resources/` (e apagar o
  job criado pela UI pra evitar duplicata) quando a criacao via API voltar
  a funcionar.
