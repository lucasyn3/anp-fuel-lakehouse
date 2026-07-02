import pytest
from download_anp import download_latest, download_month, latest_url, monthly_url, parse_args


def test_monthly_url_pads_month():
    url = monthly_url(2025, 1, "diesel-gnv")
    assert url == (
        "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
        "arquivos/shpc/dsan/2025/precos-diesel-gnv-01.csv"
    )


def test_monthly_url_unknown_product_raises():
    with pytest.raises(KeyError):
        monthly_url(2025, 1, "querosene")


def test_latest_url():
    url = latest_url("glp")
    assert url == (
        "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
        "arquivos/shpc/qus/ultimas-4-semanas-glp.csv"
    )


def test_parse_args_requires_year_or_latest():
    args = parse_args([])
    assert args.year is None
    assert args.latest is False


def test_parse_args_month_can_repeat():
    args = parse_args(["--year", "2025", "--month", "1", "--month", "2"])
    assert args.month == [1, 2]


def test_download_month_calls_download_once_per_product(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(
        "download_anp.download",
        lambda url, dest, **kwargs: calls.append((url, dest)),
    )

    download_month(2025, 3, tmp_path)

    assert len(calls) == 3
    urls = {url for url, _ in calls}
    assert urls == {
        monthly_url(2025, 3, "diesel-gnv"),
        monthly_url(2025, 3, "gasolina-etanol"),
        monthly_url(2025, 3, "glp"),
    }
    dests = {dest for _, dest in calls}
    assert dests == {
        tmp_path / "2025" / "diesel-gnv-03.csv",
        tmp_path / "2025" / "gasolina-etanol-03.csv",
        tmp_path / "2025" / "glp-03.csv",
    }


def test_download_latest_calls_download_once_per_product(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(
        "download_anp.download",
        lambda url, dest, **kwargs: calls.append((url, dest)),
    )

    download_latest(tmp_path)

    assert len(calls) == 3
    dests = {dest for _, dest in calls}
    assert dests == {
        tmp_path / "latest" / "diesel-gnv.csv",
        tmp_path / "latest" / "gasolina-etanol.csv",
        tmp_path / "latest" / "glp.csv",
    }
