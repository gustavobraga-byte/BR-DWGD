#!/usr/bin/env python3
"""
calcular_normal.py
------------------
Calcula normais climatológicas (média de 30 anos) a partir dos dados
Brazilian Daily Weather Gridded Data (BR-DWGD).

Resolução espacial: 0.1° × 0.1° (obrigatória, nunca reamostrada)

Uso:
    python calcular_normal.py \
        --arquivo pr_BR-DWGD_UFES_UTEXAS_v_3.2.3_19610101_20240320.nc \
        --variavel pr \
        --ano_inicio 1991 \
        --ano_fim 2020 \
        --escala mensal \
        --saida normal_pr_1991_2020.nc

Citação obrigatória dos dados:
    Xavier, A. C. et al. (2022). Int. J. Climatol., 42(16), 8390–8404.
    https://doi.org/10.1002/joc.7731
"""

import argparse
import sys
import numpy as np
import xarray as xr


# ---------------------------------------------------------------------------
# Variáveis acumuladas (usar soma para agregar) vs. médias
# ---------------------------------------------------------------------------
VARIAVEIS_ACUMULADAS = {"pr", "ETo"}

VARIAVEIS_VALIDAS = {"pr", "Tmax", "Tmin", "Rs", "RH", "u2", "ETo"}


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def verificar_resolucao(ds: xr.Dataset, nome: str = "dataset") -> None:
    """Garante que a grade seja 0.1° × 0.1°. Lança ValueError se não for."""
    lat_res = abs(float(ds.latitude.diff("latitude").mean()))
    lon_res = abs(float(ds.longitude.diff("longitude").mean()))
    ok = abs(lat_res - 0.1) < 1e-4 and abs(lon_res - 0.1) < 1e-4
    if not ok:
        raise ValueError(
            f"[{nome}] Resolução incorreta: {lat_res:.5f}° × {lon_res:.5f}°. "
            "BR-DWGD exige exatamente 0.1° × 0.1°. "
            "Não faça reamostragm dos dados."
        )
    print(f"[{nome}] ✓ Resolução 0.1° × 0.1° confirmada")


def validar_periodo_30_anos(ano_inicio: int, ano_fim: int) -> None:
    """Verifica se o período tem exatamente 30 anos."""
    n_anos = ano_fim - ano_inicio + 1
    if n_anos != 30:
        raise ValueError(
            f"A normal climatológica requer exatamente 30 anos. "
            f"Período informado: {ano_inicio}–{ano_fim} ({n_anos} anos)."
        )
    print(f"✓ Período válido: {ano_inicio}–{ano_fim} (30 anos)")


def abrir_dataset(arquivo: str) -> xr.Dataset:
    """Abre o NetCDF e verifica a resolução espacial."""
    print(f"Abrindo: {arquivo}")
    ds = xr.open_dataset(arquivo, chunks={"time": 365})
    verificar_resolucao(ds, arquivo)
    return ds


# ---------------------------------------------------------------------------
# Cálculo das normais
# ---------------------------------------------------------------------------

def calcular_normal_mensal(
    ds: xr.Dataset,
    variavel: str,
    ano_inicio: int,
    ano_fim: int,
) -> xr.DataArray:
    """
    Calcula a normal climatológica mensal (12 valores por pixel).

    Para variáveis acumuladas (pr, ETo):
        normal_mes_m = média dos 30 anos de [soma_diária_do_mes_m]

    Para variáveis médias (Tmax, Tmin, Rs, RH, u2):
        normal_mes_m = média dos 30 anos de [média_diária_do_mes_m]
    """
    da = ds[variavel].sel(time=slice(f"{ano_inicio}-01-01", f"{ano_fim}-12-31"))

    if variavel in VARIAVEIS_ACUMULADAS:
        # Soma mensal para cada ano, depois média entre os 30 anos
        mensal_por_ano = da.resample(time="ME").sum()
        normal = mensal_por_ano.groupby("time.month").mean(dim="time")
        metodo_str = "soma_mensal_media_30anos"
    else:
        # Média mensal para cada ano, depois média entre os 30 anos
        mensal_por_ano = da.resample(time="ME").mean()
        normal = mensal_por_ano.groupby("time.month").mean(dim="time")
        metodo_str = "media_mensal_media_30anos"

    normal.name = variavel
    normal.attrs.update({
        "long_name": f"Normal climatológica mensal de {variavel} ({ano_inicio}-{ano_fim})",
        "units": ds[variavel].attrs.get("units", ""),
        "periodo_normal": f"{ano_inicio}-{ano_fim}",
        "metodo": metodo_str,
        "resolucao_espacial": "0.1 grau",
        "fonte": "BR-DWGD (Xavier et al., 2022) — doi:10.1002/joc.7731",
    })
    return normal


def calcular_normal_anual(
    ds: xr.Dataset,
    variavel: str,
    ano_inicio: int,
    ano_fim: int,
) -> xr.DataArray:
    """
    Calcula a normal climatológica anual (1 valor por pixel).

    Para variáveis acumuladas (pr, ETo):
        normal_anual = média dos 30 anos de [soma_anual]

    Para variáveis médias:
        normal_anual = média dos 30 anos de [média_anual]
    """
    da = ds[variavel].sel(time=slice(f"{ano_inicio}-01-01", f"{ano_fim}-12-31"))

    if variavel in VARIAVEIS_ACUMULADAS:
        anual_por_ano = da.resample(time="YE").sum()
        metodo_str = "soma_anual_media_30anos"
    else:
        anual_por_ano = da.resample(time="YE").mean()
        metodo_str = "media_anual_media_30anos"

    normal = anual_por_ano.mean(dim="time")
    normal.name = variavel
    normal.attrs.update({
        "long_name": f"Normal climatológica anual de {variavel} ({ano_inicio}-{ano_fim})",
        "units": ds[variavel].attrs.get("units", ""),
        "periodo_normal": f"{ano_inicio}-{ano_fim}",
        "metodo": metodo_str,
        "resolucao_espacial": "0.1 grau",
        "fonte": "BR-DWGD (Xavier et al., 2022) — doi:10.1002/joc.7731",
    })
    return normal


# ---------------------------------------------------------------------------
# Recorte espacial (opcional)
# ---------------------------------------------------------------------------

def recortar_bbox(
    ds: xr.Dataset,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
) -> xr.Dataset:
    """
    Recorta o dataset por bounding box, preservando a grade 0.1° × 0.1°.
    O arquivo BR-DWGD tem latitude decrescente (sul → norte no índice).
    """
    ds_rec = ds.sel(
        latitude=slice(lat_max, lat_min),
        longitude=slice(lon_min, lon_max),
    )
    verificar_resolucao(ds_rec, "recorte_bbox")
    return ds_rec


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Calcula normais climatológicas (30 anos) do BR-DWGD."
    )
    p.add_argument("--arquivo", required=True, help="Caminho para o arquivo NetCDF do BR-DWGD")
    p.add_argument(
        "--variavel", required=True,
        choices=sorted(VARIAVEIS_VALIDAS),
        help="Variável a processar",
    )
    p.add_argument("--ano_inicio", type=int, required=True, help="Ano inicial (ex.: 1991)")
    p.add_argument("--ano_fim", type=int, required=True, help="Ano final (ex.: 2020)")
    p.add_argument(
        "--escala", choices=["mensal", "anual"], default="mensal",
        help="Escala temporal da normal (padrão: mensal)",
    )
    p.add_argument("--saida", default="normal_output.nc", help="Arquivo NetCDF de saída")

    # Recorte espacial opcional
    p.add_argument("--lat_min", type=float, default=None)
    p.add_argument("--lat_max", type=float, default=None)
    p.add_argument("--lon_min", type=float, default=None)
    p.add_argument("--lon_max", type=float, default=None)

    return p.parse_args()


def main():
    args = parse_args()

    # 1. Validar período
    validar_periodo_30_anos(args.ano_inicio, args.ano_fim)

    # 2. Abrir e verificar resolução
    ds = abrir_dataset(args.arquivo)

    # 3. Recorte espacial opcional
    bbox_args = [args.lat_min, args.lat_max, args.lon_min, args.lon_max]
    if any(v is not None for v in bbox_args):
        if not all(v is not None for v in bbox_args):
            print("ERRO: informe --lat_min, --lat_max, --lon_min e --lon_max juntos.")
            sys.exit(1)
        ds = recortar_bbox(ds, args.lat_min, args.lat_max, args.lon_min, args.lon_max)

    # 4. Calcular normal
    print(f"Calculando normal {args.escala} de {args.variavel} "
          f"para {args.ano_inicio}–{args.ano_fim}...")

    if args.escala == "mensal":
        normal = calcular_normal_mensal(ds, args.variavel, args.ano_inicio, args.ano_fim)
    else:
        normal = calcular_normal_anual(ds, args.variavel, args.ano_inicio, args.ano_fim)

    # 5. Verificar resolução do resultado
    if "latitude" in normal.dims and "longitude" in normal.dims:
        ds_out = normal.to_dataset()
        verificar_resolucao(ds_out, "saida")

    # 6. Salvar
    normal.to_netcdf(args.saida)
    print(f"✓ Normal salva em: {args.saida}")
    print("\n--- Resumo ---")
    print(normal)
    print("\nLembre-se de citar:")
    print("  Xavier et al. (2022) Int. J. Climatol. 42(16), 8390–8404.")
    print("  https://doi.org/10.1002/joc.7731")


if __name__ == "__main__":
    main()
