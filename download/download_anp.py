"""Baixa os CSVs de precos de combustiveis publicados pela ANP.

Fonte: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis

Uso:
    python download_anp.py --year 2025 --month 1 --month 2
    python download_anp.py --year 2025 --all-months
    python download_anp.py --latest
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

BASE_URL = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc"

MONTHLY_PRODUCTS = {
    "diesel-gnv": "precos-diesel-gnv-{month:02d}.csv",
    "gasolina-etanol": "precos-gasolina-etanol-{month:02d}.csv",
    "glp": "precos-glp-{month:02d}.csv",
}

LATEST_PRODUCTS = ("diesel-gnv", "gasolina-etanol", "glp")


def monthly_url(year: int, month: int, product: str) -> str:
    filename = MONTHLY_PRODUCTS[product].format(month=month)
    return f"{BASE_URL}/dsan/{year}/{filename}"


def latest_url(product: str) -> str:
    return f"{BASE_URL}/qus/ultimas-4-semanas-{product}.csv"


def download(url: str, dest: Path, *, timeout: int = 60) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"OK  {url} -> {dest} ({len(response.content)} bytes)")


def download_month(year: int, month: int, out_dir: Path) -> None:
    for product in MONTHLY_PRODUCTS:
        url = monthly_url(year, month, product)
        dest = out_dir / f"{year}" / f"{product}-{month:02d}.csv"
        download(url, dest)


def download_latest(out_dir: Path) -> None:
    for product in LATEST_PRODUCTS:
        url = latest_url(product)
        dest = out_dir / "latest" / f"{product}.csv"
        download(url, dest)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, help="Ano da serie mensal (ex: 2025)")
    parser.add_argument(
        "--month",
        type=int,
        action="append",
        help="Mes da serie mensal, 1-12. Pode ser repetido. Requer --year.",
    )
    parser.add_argument(
        "--all-months",
        action="store_true",
        help="Baixa os 12 meses do --year informado.",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Baixa o arquivo de ultimas 4 semanas para cada produto.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "data",
        help="Diretorio de saida (default: download/data).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.latest and not args.year:
        print("Informe --year (com --month/--all-months) ou --latest.", file=sys.stderr)
        return 2

    if args.latest:
        download_latest(args.out_dir)

    if args.year:
        months = range(1, 13) if args.all_months else (args.month or [])
        if not months:
            print("Informe --month (um ou mais) ou --all-months junto com --year.", file=sys.stderr)
            return 2
        for month in months:
            download_month(args.year, month, args.out_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
