from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_date, trim

dp.create_streaming_table(name="anp_lakehouse.silver.revendas")


@dp.temporary_view(name="revendas_observadas")
def revendas_observadas():
    return spark.readStream.table("anp_lakehouse.bronze.precos_combustiveis").select(
        trim(col("cnpj_revenda")).alias("cnpj_revenda"),
        trim(col("revenda")).alias("revenda"),
        trim(col("bandeira")).alias("bandeira"),
        trim(col("nome_rua")).alias("nome_rua"),
        trim(col("numero_rua")).alias("numero_rua"),
        trim(col("bairro")).alias("bairro"),
        trim(col("cep")).alias("cep"),
        trim(col("municipio")).alias("municipio"),
        trim(col("estado_sigla")).alias("estado_sigla"),
        to_date(col("data_coleta"), "dd/MM/yyyy").alias("data_coleta"),
    )


dp.create_auto_cdc_flow(
    target="anp_lakehouse.silver.revendas",
    source="revendas_observadas",
    keys=["cnpj_revenda"],
    sequence_by="data_coleta",
    stored_as_scd_type=2,
    track_history_column_list=["bandeira", "revenda", "nome_rua", "numero_rua", "bairro"],
)
