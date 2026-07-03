# resources/disabled/

Recursos de bundle escritos mas fora do deploy ativo (o `databricks.yml`
inclui so `resources/*.yml`, essa pasta nao entra no glob).

- `anp_job.job.yml`: falha em `databricks bundle deploy` com "Organization
  ... has been cancelled or is not active yet" (403) ao criar o Job, mesmo
  com o pipeline e o resto do bundle funcionando. Sem Account Console no
  Free Edition pra diagnosticar a causa. Mover de volta pra `resources/`
  quando o erro parar de acontecer.
