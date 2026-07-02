from pyspark import pipelines as dp
from pyspark.sql.functions import col, current_timestamp

LANDING_PATH = "/Volumes/anp_lakehouse/bronze/landing"
SCHEMA_LOCATION = "/Volumes/anp_lakehouse/bronze/landing/_schema/precos_combustiveis"

RAW_TO_CLEAN_COLUMNS = {
    "Regiao - Sigla": "regiao_sigla",
    "Estado - Sigla": "estado_sigla",
    "Municipio": "municipio",
    "Revenda": "revenda",
    "CNPJ da Revenda": "cnpj_revenda",
    "Nome da Rua": "nome_rua",
    "Numero Rua": "numero_rua",
    "Complemento": "complemento",
    "Bairro": "bairro",
    "Cep": "cep",
    "Produto": "produto",
    "Data da Coleta": "data_coleta",
    "Valor de Venda": "valor_venda",
    "Valor de Compra": "valor_compra",
    "Unidade de Medida": "unidade_medida",
    "Bandeira": "bandeira",
}


@dp.table(
    name="precos_combustiveis",
    comment="Ingestao incremental via Auto Loader dos CSVs de precos da ANP.",
)
@dp.expect("produto_presente", "produto IS NOT NULL")
@dp.expect("valor_venda_presente", "valor_venda IS NOT NULL")
def precos_combustiveis():
    df = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", SCHEMA_LOCATION)
        .option("header", "true")
        .option("delimiter", ";")
        .option("encoding", "UTF-8")
        .load(LANDING_PATH)
    )
    for raw_name, clean_name in RAW_TO_CLEAN_COLUMNS.items():
        df = df.withColumnRenamed(raw_name, clean_name)
    return df.withColumn("_ingested_at", current_timestamp()).withColumn(
        "_source_file", col("_metadata.file_path")
    )
