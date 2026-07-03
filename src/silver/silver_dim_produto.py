from pyspark import pipelines as dp

PRODUTOS = [
    (1, "DIESEL", "Diesel"),
    (2, "DIESEL S10", "Diesel"),
    (3, "GASOLINA", "Gasolina"),
    (4, "GASOLINA ADITIVADA", "Gasolina"),
    (5, "ETANOL", "Etanol"),
    (6, "GLP", "GLP"),
    (7, "GNV", "GNV"),
]

SCHEMA = "produto_id INT, produto_nome STRING, categoria STRING"


@dp.materialized_view(
    name="anp_lakehouse.silver.dim_produto",
    comment="Dimensao de produtos de combustivel. Dominio fixo e conhecido (ver README).",
)
def dim_produto():
    return spark.createDataFrame(PRODUTOS, schema=SCHEMA)
