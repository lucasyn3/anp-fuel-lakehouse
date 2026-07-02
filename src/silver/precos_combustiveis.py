from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql.functions import col, regexp_replace, row_number, to_date, trim


@dp.materialized_view(
    name="anp_lakehouse.silver.precos_combustiveis",
    comment="Precos de combustiveis limpos, deduplicados e com tipos corretos.",
)
@dp.expect_or_drop("valor_venda_valido", "valor_venda IS NOT NULL AND valor_venda > 0")
@dp.expect_or_drop("data_coleta_valida", "data_coleta IS NOT NULL AND data_coleta <= current_date()")
@dp.expect("produto_conhecido", "produto IN ('DIESEL', 'DIESEL S10', 'GASOLINA', 'GASOLINA ADITIVADA', 'ETANOL', 'GLP', 'GNV')")
def precos_combustiveis():
    df = spark.read.table("anp_lakehouse.bronze.precos_combustiveis").select(
        trim(col("cnpj_revenda")).alias("cnpj_revenda"),
        trim(col("produto")).alias("produto"),
        to_date(col("data_coleta"), "dd/MM/yyyy").alias("data_coleta"),
        regexp_replace(col("valor_venda"), ",", ".").cast("decimal(10,3)").alias("valor_venda"),
        regexp_replace(col("valor_compra"), ",", ".").cast("decimal(10,3)").alias("valor_compra"),
        trim(col("unidade_medida")).alias("unidade_medida"),
        trim(col("regiao_sigla")).alias("regiao_sigla"),
        trim(col("estado_sigla")).alias("estado_sigla"),
        trim(col("municipio")).alias("municipio"),
        col("_ingested_at"),
    )

    dedup_key = ["cnpj_revenda", "produto", "data_coleta"]
    window = Window.partitionBy(*dedup_key).orderBy(col("_ingested_at").desc())
    return (
        df.withColumn("_rn", row_number().over(window))
        .filter(col("_rn") == 1)
        .drop("_rn", "_ingested_at")
    )
