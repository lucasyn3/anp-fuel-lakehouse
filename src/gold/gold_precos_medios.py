from pyspark import pipelines as dp
from pyspark.sql.functions import avg, broadcast, col, count, date_trunc
from pyspark.sql.functions import max as spark_max
from pyspark.sql.functions import min as spark_min


@dp.materialized_view(
    name="anp_lakehouse.gold.precos_medios",
    comment="Preco medio de combustiveis por estado, produto e mes.",
)
def precos_medios():
    fato = spark.read.table("anp_lakehouse.silver.precos_combustiveis")
    produtos = spark.read.table("anp_lakehouse.silver.produtos")

    return (
        fato.join(broadcast(produtos), "produto_id")
        .withColumn("mes_referencia", date_trunc("month", col("data_coleta")).cast("date"))
        .groupBy("estado_sigla", "produto_nome", "categoria", "mes_referencia")
        .agg(
            avg("valor_venda").alias("preco_medio"),
            spark_min("valor_venda").alias("preco_minimo"),
            spark_max("valor_venda").alias("preco_maximo"),
            count("*").alias("qtd_observacoes"),
        )
    )
