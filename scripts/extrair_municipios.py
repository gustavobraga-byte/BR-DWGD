#!/usr/bin/env python3
"""
extrair_municipios.py
---------------------
Extrai séries temporais municipais de variáveis climáticas BR-DWGD a partir
de arquivos mensais agregados (NetCDF), usando ponderação por área de interseção
entre pixels de 0.1° e polígonos dos municípios.

Resolução espacial: 0.1° × 0.1° (preservada)
Dados de entrada: arquivos mensais v3.2.4 (~5 MB cada)
Saída: CSV municipio × ano com médias ponderadas por área.

Uso:
    python extrair_municipios.py \
        --dir_dados /tmp/monthly_data \
        --gpkg /caminho/municipios.gpkg \
        --layer_camada cod_ibge \
        --coluna_cod CD_MUN \
        --variaveis Tmax Tmin Tmean Pr ETo RH \
        --ano_inicio 1961 --ano_fim 2025 \
        --saida clima_municipal.csv

Citação:
    Xavier et al. (2022) Int. J. Climatol. doi:10.1002/joc.7731
"""
import argparse, sys, warnings, os
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from shapely.geometry import box
from rasterio import features
from datetime import datetime

warnings.filterwarnings("ignore")

# Mapeamento: chave usada no código → (nome no NetCDF, é_acumulada)
VAR_CONFIG = {
    "Tmax":        ("Tmax",  False),
    "Tmin":        ("Tmin",  False),
    "Tmean":       ("Tmean", False),  # existe nos mensais; calcular se não existir
    "Pr":          ("pr",    True),   # precipitação: soma anual
    "ETo":         ("ETo",   True),   # ETo mensal já é total (mm/mês)
    "RH":          ("RH",    False),
    "RH_15set_15nov": ("RH", False),  # mesmo NetCDF, agregação especial
    "Rs":          ("Rs",    False),
    "u2":          ("u2",    False),
}

def area_weighted_mean(grid_2d, lats, lons, mun_polygon, mun_crs="EPSG:4674"):
    """Calcula média ponderada por área de interseção pixel × município."""
    gdf_pixels = gpd.GeoDataFrame(
        {"value": grid_2d.flatten(),
         "geometry": [box(lons[j], lats[i+1], lons[j+1], lats[i])
                      for i in range(len(lats)-1) for j in range(len(lons)-1)]},
        crs=mun_crs
    )
    # Remover pixels sem interseção
    mask = gdf_pixels.intersects(mun_polygon)
    if not mask.any():
        return np.nan
    gdf_pixels = gdf_pixels[mask].copy()

    # Projetar para área planar (Policônica Brasil)
    gdf_proj = gdf_pixels.to_crs("EPSG:5880")
    mun_proj = gpd.GeoDataFrame(geometry=[mun_polygon], crs=mun_crs).to_crs("EPSG:5880")

    areas = gdf_proj.intersection(mun_proj.geometry.iloc[0]).area
    total = areas.sum()
    if total == 0:
        return np.nan
    return float(np.average(gdf_proj["value"], weights=areas))


def compute_annual(var_key, ds, ano_ini, ano_fim):
    """Retorna dict {ano: array 2D} para cada ano no período."""
    nc_name, is_acc = VAR_CONFIG[var_key]
    da = ds[nc_name]
    time_idx = da.time.values
    anos = pd.DatetimeIndex(time_idx).year
    anos_unicos = sorted(a for a in np.unique(anos) if ano_ini <= a <= ano_fim)

    result = {}
    for yr in anos_unicos:
        mask = anos == yr
        vals = da.values[mask]
        if is_acc:
            result[yr] = vals.sum(axis=0)
        else:
            result[yr] = vals.mean(axis=0)
    return result


def compute_rh_sep_nov(ds, ano_ini, ano_fim):
    """Média ponderada 15-set a 15-nov: 0.25*set + 0.5*out + 0.25*nov."""
    da = ds["RH"]
    anos = pd.DatetimeIndex(da.time.values).year
    meses = pd.DatetimeIndex(da.time.values).month
    result = {}
    for ano in range(ano_ini, ano_fim + 1):
        mask = anos == ano
        if mask.sum() == 0:
            continue
        vals = da.values[mask]
        m = meses[mask]
        set_vals = vals[m == 9]
        out_vals = vals[m == 10]
        nov_vals = vals[m == 11]
        if len(set_vals) == 0 or len(out_vals) == 0 or len(nov_vals) == 0:
            continue
        result[ano] = 0.25 * set_vals[0] + 0.50 * out_vals[0] + 0.25 * nov_vals[0]
    return result


def main():
    p = argparse.ArgumentParser(description="Extrai séries climáticas municipais do BR-DWGD.")
    p.add_argument("--dir_dados", required=True, help="Diretório com arquivos NetCDF mensais")
    p.add_argument("--gpkg", required=True, help="GeoPackage com municípios")
    p.add_argument("--layer_camada", default=None, help="Nome da camada no GPKG")
    p.add_argument("--coluna_cod", default="CD_MUN", help="Coluna com código IBGE")
    p.add_argument("--coluna_geom", default="geometry", help="Coluna de geometria")
    p.add_argument("--variaveis", nargs="+", default=["Tmax", "Tmin", "Pr", "ETo", "RH"],
                   help="Variáveis a processar")
    p.add_argument("--ano_inicio", type=int, default=1961)
    p.add_argument("--ano_fim", type=int, default=2025)
    p.add_argument("--saida", default="clima_municipal.csv")
    p.add_argument("--bbox", nargs=4, type=float, default=None,
                   help="lon_min lat_min lon_max lat_max (opcional)")
    args = p.parse_args()

    print("=== Extração Municipal BR-DWGD ===")
    print(f"Variáveis: {args.variaveis}")
    print(f"Período: {args.ano_inicio}–{args.ano_fim}")

    # 1. Carregar municípios
    kwargs = {}
    if args.layer_camada:
        kwargs["layer"] = args.layer_camada
    gdf = gpd.read_file(args.gpkg, **kwargs)
    gdf = gdf.to_crs("EPSG:4674")

    if args.bbox:
        lon_min, lat_min, lon_max, lat_max = args.bbox
        gdf = gdf.cx[lon_min:lon_max, lat_min:lat_max]
    print(f"Municípios: {len(gdf)}")

    # 2. Abrir dados e obter grid
    lats, lons = None, None
    datasets = {}
    rh_needed = "RH_15set_15nov" in args.variaveis or "RH" in args.variaveis
    tmean_needed = "Tmean" in args.variaveis

    for var_key in args.variaveis:
        if var_key == "RH_15set_15nov":
            fn = os.path.join(args.dir_dados, "RH_1961_2025_BR-DWGD_monthly_v_3.2.4.nc")
        elif var_key == "Tmean" and not os.path.exists(
                os.path.join(args.dir_dados, "Tmean_1961_2025_BR-DWGD_monthly_v_3.2.4.nc")):
            # Calcular a partir de Tmax + Tmin
            continue
        else:
            nc_name, _ = VAR_CONFIG[var_key]
            fn = os.path.join(args.dir_dados, f"{nc_name}_1961_2025_BR-DWGD_monthly_v_3.2.4.nc")
        if not os.path.exists(fn):
            print(f"  ⚠ Arquivo não encontrado: {fn}")
            continue
        datasets[var_key] = xr.open_dataset(fn)
        ds = datasets[var_key]
        if lats is None:
            lats = ds.latitude.values
            lons = ds.longitude.values
            print(f"Grade: {len(lats)} lat × {len(lons)} lon ({len(lats)-1}×{len(lons)-1} pixels)")

    # Tmean via Tmax + Tmin se não existir arquivo separado
    if tmean_needed and "Tmean" not in datasets:
        print("  Tmean calculada como (Tmax + Tmin) / 2")
        ds_tmax = xr.open_dataset(os.path.join(args.dir_dados, "Tmax_1961_2025_BR-DWGD_monthly_v_3.2.4.nc"))
        ds_tmin = xr.open_dataset(os.path.join(args.dir_dados, "Tmin_1961_2025_BR-DWGD_monthly_v_3.2.4.nc"))

    # 3. Extrair para cada município
    rows = []
    for idx_mun, (_, mun_row) in enumerate(gdf.iterrows()):
        cod = mun_row[args.coluna_cod]
        poly = mun_row[args.coluna_geom]
        if idx_mun % 10 == 0:
            print(f"  Município {idx_mun+1}/{len(gdf)}: {cod}")

        for var_key in args.variaveis:
            if var_key == "Tmean" and "Tmean" not in datasets:
                # Calcular de Tmax + Tmin
                vals = compute_annual("Tmax", ds_tmax, args.ano_inicio, args.ano_fim)
                vals2 = compute_annual("Tmin", ds_tmin, args.ano_inicio, args.ano_fim)
                for ano in sorted(vals.keys()):
                    if ano not in vals2:
                        continue
                    grid = (vals[ano] + vals2[ano]) / 2.0
                    rows.append({
                        "CD_MUN": cod, "ANO": ano, "VARIAVEL": "Tmean",
                        "VALOR": area_weighted_mean(grid, lats, lons, poly)
                    })
                continue

            if var_key == "RH_15set_15nov":
                vals = compute_rh_sep_nov(datasets["RH"], args.ano_inicio, args.ano_fim)
                for ano, grid in sorted(vals.items()):
                    rows.append({
                        "CD_MUN": cod, "ANO": ano, "VARIAVEL": "RH_15set_15nov",
                        "VALOR": area_weighted_mean(grid, lats, lons, poly)
                    })
                continue

            ds = datasets.get(var_key)
            if ds is None:
                continue
            vals = compute_annual(var_key, ds, args.ano_inicio, args.ano_fim)
            for ano, grid in sorted(vals.items()):
                rows.append({
                    "CD_MUN": cod, "ANO": ano, "VARIAVEL": var_key,
                    "VALOR": area_weighted_mean(grid, lats, lons, poly)
                })

    # 4. Fechar datasets
    for ds in datasets.values():
        ds.close()
    if tmean_needed and "Tmean" not in datasets:
        ds_tmax.close()
        ds_tmin.close()

    # 5. Pivotar para formato largo (coluna por variável)
    df = pd.DataFrame(rows)
    df_pivot = df.pivot_table(
        index=["CD_MUN", "ANO"], columns="VARIAVEL", values="VALOR"
    ).reset_index()
    df_pivot.columns.name = None

    df_pivot.to_csv(args.saida, index=False)
    print(f"\n✓ Salvo: {args.saida} ({len(df_pivot)} linhas, {len(df_pivot.columns)-2} variáveis)")
    print(f"  Período: {df_pivot.ANO.min()}–{df_pivot.ANO.max()}")
    print(f"  Municípios: {df_pivot.CD_MUN.nunique()}")


if __name__ == "__main__":
    main()
