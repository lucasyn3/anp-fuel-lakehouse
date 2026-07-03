from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql.functions import broadcast, col, regexp_replace, row_number, to_date, trim


@dp.materialized_view(
    name="anp_lakehouse.silver.precos_combustiveis",
    comment="Precos de combustiveis limpos, deduplicados e com tipos corretos. produto_id referencia silver.dim_produto.",
)
@dp.expect_or_drop("valor_venda_valido", "valor_venda IS NOT NULL AND valor_venda > 0")
@dp.expect_or_drop("data_coleta_valida", "data_coleta IS NOT NULL AND data_coleta <= current_date()")
@dp.expect_or_drop("produto_conhecido", "produto_id IS NOT NULL")
def precos_combustiveis():
    bronze = spark.read.table("anp_lakehouse.bronze.precos_combustiveis")
    dim_produto = spark.read.table("anp_lakehouse.silver.dim_produto")

    df = (
        bronze.join(
            broadcast(dim_produto),
            trim(bronze["produto"]) == dim_produto["produto_nome"],
            "left",
        ).select(
            trim(bronze["cnpj_revenda"]).alias("cnpj_revenda"),
            dim_produto["produto_id"],
            to_date(bronze["data_coleta"], "dd/MM/yyyy").alias("data_coleta"),
            regexp_replace(bronze["valor_venda"], ",", ".").cast("decimal(10,3)").alias("valor_venda"),
            regexp_replace(bronze["valor_compra"], ",", ".").cast("decimal(10,3)").alias("valor_compra"),
            trim(bronze["unidade_medida"]).alias("unidade_medida"),
            trim(bronze["regiao_sigla"]).alias("regiao_sigla"),
            trim(bronze["estado_sigla"]).alias("estado_sigla"),
            trim(bronze["municipio"]).alias("municipio"),
            bronze["_ingested_at"],
        )
    )

    dedup_key = ["cnpj_revenda", "produto_id", "data_coleta"]
    window = Window.partitionBy(*dedup_key).orderBy(col("_ingested_at").desc())
    return (
        df.withColumn("_rn", row_number().over(window))
        .filter(col("_rn") == 1)
        .drop("_rn", "_ingested_at")
    )
