#!/usr/bin/env python3
"""
gerar_mapa_normal_padrao.py  ──  PesquisAI Standard Normal Map Generator
=========================================================================
Gera mapas de normais climatológicas do BR-DWGD seguindo o padrão definitivo:

  ✅ Reamostragem bilinear (imshow, interpolation='bilinear') — sem grid visível
  ✅ Hierarquia de limites: municípios (cinza fino) + região dissolvida (preto grosso)
  ✅ Títulos, legendas e colorbars em INGLÊS
  ✅ Mapas de comparação 3×3 com fontes GRANDES
  ✅ BH = Pr − ETo × 1,05 (coeficiente de cultivo Kc)
  ✅ 11 períodos deslizantes (1975…2025) × 6 variáveis = 66 mapas individuais
  ✅ 6 mapas de comparação de diferenças consecutivas

Uso:
    python scripts/gerar_mapa_normal_padrao.py \
        --zip_pr /caminho/pr_Tmax_Tmin_NetCDF_Files.zip \
        --zip_eto /caminho/ETo_u2_RH_Rs_NetCDF_Files.zip \
        --gpkg /caminho/MUN_MATAS.gpkg \
        --saida /caminho/output_dir/ \
        --lat_min -21.5 --lat_max -19.0 \
        --lon_min -43.8 --lon_max -41.0 \
        [--dpi 250] \
        [--idioma en] \
        [--kc 1.05]

Citação obrigatória dos dados:
    Xavier, A. C. et al. (2022). Int. J. Climatol., 42(16), 8390–8404.
    https://doi.org/10.1002/joc.7731
=========================================================================
"""

import os, sys, zipfile, gc, warnings, argparse
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

warnings.filterwarnings('ignore')

# ====================================================================
# CONFIGURAÇÕES PADRÃO
# ====================================================================

PERIODOS_PADRAO = [
    (1961, 1974), (1961, 1979), (1961, 1984), (1961, 1989),
    (1965, 1994), (1970, 1999), (1975, 2004), (1980, 2009),
    (1985, 2014), (1990, 2019), (1995, 2024),
]

# Rótulos das comparações: 1980, 1985, ..., 2025
COMP_LABELS = [str(y) for y in range(1980, 2026, 5)]

VARIAVEIS = {
    'Tmean': {
        'label': 'Mean Temperature (°C)',
        'cmap': 'Reds',
        'tipo': 'media',
        'derived': True,
        'formula': 'lambda tmax, tmin, pr, eto: (tmax + tmin) / 2.0',
    },
    'Tmax': {
        'label': 'Maximum Temperature (°C)',
        'cmap': 'Reds',
        'tipo': 'media',
        'derived': False,
    },
    'Tmin': {
        'label': 'Minimum Temperature (°C)',
        'cmap': 'Blues',
        'tipo': 'media',
        'derived': False,
    },
    'Pr': {
        'label': 'Precipitation (mm)',
        'cmap': 'Blues',
        'tipo': 'soma',
        'derived': False,
    },
    'ETo': {
        'label': 'Reference Evapotranspiration (mm)',
        'cmap': 'YlGn',
        'tipo': 'soma',
        'derived': False,
    },
    'BH': {
        'label': 'Water Balance (mm)',
        'cmap': 'BrBG',
        'tipo': 'soma',
        'derived': True,
        'formula': 'lambda tmax, tmin, pr, eto: pr - eto * KC',
    },
}

VAR_EN = {
    'Tmean': 'Mean Temperature',
    'Tmax': 'Maximum Temperature',
    'Tmin': 'Minimum Temperature',
    'Pr': 'Precipitation',
    'ETo': 'Reference Evapotranspiration',
    'BH': 'Water Balance',
}

# ====================================================================
# FUNÇÕES
# ====================================================================

def parse_args():
    p = argparse.ArgumentParser(
        description='PesquisAI — Geração de mapas de normais climatológicas BR-DWGD'
    )
    p.add_argument('--zip_pr', required=True,
                   help='Caminho para pr_Tmax_Tmin_NetCDF_Files.zip')
    p.add_argument('--zip_eto', required=True,
                   help='Caminho para ETo_u2_RH_Rs_NetCDF_Files.zip')
    p.add_argument('--gpkg', required=True,
                   help='Caminho para GeoPackage dos municípios')
    p.add_argument('--saida', required=True,
                   help='Diretório de saída para os JPEGs')
    p.add_argument('--lat_min', type=float, required=True)
    p.add_argument('--lat_max', type=float, required=True)
    p.add_argument('--lon_min', type=float, required=True)
    p.add_argument('--lon_max', type=float, required=True)
    p.add_argument('--dpi', type=int, default=200,
                   help='DPI das figuras (padrão: 200)')
    p.add_argument('--kc', type=float, default=1.05,
                   help='Coeficiente de cultivo Kc para BH (padrão: 1.05)')
    p.add_argument('--idioma', choices=['en', 'pt'], default='en',
                   help='Idioma dos títulos (padrão: en)')
    p.add_argument('--extracao', default='/tmp/brdwgd_extract_std',
                   help='Diretório temporário para extração')
    return p.parse_args()


def periodo_label(ano_ini, ano_fim):
    """Retorna o ano de referência (final+1) como string."""
    return str(ano_fim + 1)


def label_to_periodo(comp_label, periodos):
    """Mapeia label de comparação (ex: '1980') para tupla (ano_ini, ano_fim)."""
    ano_fim = int(comp_label) - 1
    for a0, a1 in periodos:
        if a1 == ano_fim:
            return (a0, a1)
    return None


def carregar_limites(gpkg_path):
    """Carrega municípios e dissolve para contorno da região."""
    print("=" * 60)
    print("1. Loading municipal boundaries...")
    print("=" * 60)
    gdf_mun = gpd.read_file(gpkg_path)
    gdf_mun = gdf_mun.to_crs("EPSG:4674")
    gdf_regiao = gdf_mun.dissolve()
    print(f"   {len(gdf_mun)} municipalities loaded")
    print(f"   Regional boundary created")
    return gdf_mun, gdf_regiao


def extrair_e_carregar(zip_path, nc_var_name, lat_min, lat_max,
                        lon_min, lon_max, extract_dir):
    """
    Extrai do zip, carrega com subset espacial e concatena os 3 períodos.

    Retorna xr.Dataset com dimensões (time, latitude, longitude)
    no subset especificado, já carregado em memória.
    """
    arquivos = []
    with zipfile.ZipFile(zip_path) as z:
        for f in z.namelist():
            if f.endswith('.nc') and f.startswith(nc_var_name):
                arquivos.append(f)
    arquivos.sort()

    datasets = []
    for fname in arquivos:
        with zipfile.ZipFile(zip_path) as z:
            z.extract(fname, extract_dir)
        fpath = os.path.join(extract_dir, fname)
        try:
            ds = xr.open_dataset(fpath, chunks={"time": 365})
            # Garantir ordenação crescente de latitude
            if ds.latitude.values[0] > ds.latitude.values[-1]:
                ds = ds.sortby('latitude')
            ds_sub = ds.sel(
                latitude=slice(lat_min, lat_max),
                longitude=slice(lon_min, lon_max),
            ).load()
            datasets.append(ds_sub)
            ds.close()
        except Exception as e:
            print(f"     ERROR: {fname} — {e}")
        os.remove(fpath)
        gc.collect()

    if not datasets:
        return None
    return xr.concat(datasets, dim="time")


def carregar_dados(args):
    """Carrega e prepara todos os arrays de dados."""
    print("=" * 60)
    print("2. Loading BR-DWGD data...")
    print("=" * 60)

    os.makedirs(args.extracao, exist_ok=True)

    ds_pr = extrair_e_carregar(
        args.zip_pr, 'pr',
        args.lat_min, args.lat_max, args.lon_min, args.lon_max,
        args.extracao,
    )
    ds_tmax = extrair_e_carregar(
        args.zip_pr, 'Tmax',
        args.lat_min, args.lat_max, args.lon_min, args.lon_max,
        args.extracao,
    )
    ds_tmin = extrair_e_carregar(
        args.zip_pr, 'Tmin',
        args.lat_min, args.lat_max, args.lon_min, args.lon_max,
        args.extracao,
    )
    ds_eto = extrair_e_carregar(
        args.zip_eto, 'ETo',
        args.lat_min, args.lat_max, args.lon_min, args.lon_max,
        args.extracao,
    )

    if any(d is None for d in [ds_pr, ds_tmax, ds_tmin, ds_eto]):
        print("ERROR: Failed to load required datasets!")
        sys.exit(1)

    time_idx = pd.DatetimeIndex(ds_pr.time.values)
    lats = ds_pr.latitude.values
    lons = ds_pr.longitude.values

    # Extrair arrays NumPy e calcular variáveis derivadas
    pr_data = ds_pr['pr'].values.astype(np.float32)
    tmax_data = ds_tmax['Tmax'].values.astype(np.float32)
    tmin_data = ds_tmin['Tmin'].values.astype(np.float32)
    eto_data = ds_eto['ETo'].values.astype(np.float32)
    tmean_data = (tmax_data + tmin_data) / 2.0
    bh_data = pr_data - eto_data * args.kc

    print(f"\n   Data loaded: {len(time_idx)} days, grid {len(lats)}×{len(lons)}")
    print(f"   BH = Pr - ETo × {args.kc}")

    del ds_pr, ds_tmax, ds_tmin, ds_eto
    gc.collect()

    data_map = {
        'Pr': pr_data, 'Tmax': tmax_data, 'Tmin': tmin_data,
        'Tmean': tmean_data, 'ETo': eto_data, 'BH': bh_data,
    }

    return data_map, time_idx, lats, lons


def calcular_normais(data_map, time_idx, periodos, variaveis):
    """Calcula normais para todas as variáveis × períodos."""
    print("=" * 60)
    print("3. Computing climatological normals...")
    print("=" * 60)

    def _calc(arr, tidx, a0, a1, tipo):
        mask = (tidx.year >= a0) & (tidx.year <= a1)
        anos = np.unique(tidx.year[mask])
        if tipo == 'soma':
            anuais = np.array([arr[tidx.year == y].sum(axis=0) for y in anos])
        else:
            anuais = np.array([arr[tidx.year == y].mean(axis=0) for y in anos])
        return np.mean(anuais, axis=0).astype(np.float32)

    resultados = {v: {} for v in variaveis}
    for a0, a1 in periodos:
        lbl = periodo_label(a0, a1)
        for vn, vc in variaveis.items():
            resultados[vn][lbl] = _calc(data_map[vn], time_idx, a0, a1, vc['tipo'])
        print(f"   Period {a0}-{a1} (label: {lbl})")

    return resultados


# ====================================================================
# PLOTAGEM: MAPA INDIVIDUAL
# ====================================================================

def plot_mapa_individual(valores_2d, lats, lons, var_nome, label_str,
                          saida_path, gdf_mun, gdf_regiao,
                          configuracoes, var_en, dpi, lon_min, lon_max,
                          lat_min, lat_max):
    """Gera um mapa individual com o padrão PesquisAI."""
    cfg = configuracoes[var_nome]
    fig, ax = plt.subplots(figsize=(8, 10))

    extent = [lons[0] - 0.05, lons[-1] + 0.05,
              lats[0] - 0.05, lats[-1] + 0.05]
    im = ax.imshow(valores_2d, extent=extent, origin='lower',
                   cmap=cfg['cmap'], interpolation='bilinear', aspect='auto')

    # Limites municipais (cinza fino)
    gdf_mun.boundary.plot(ax=ax, color='gray', linewidth=0.3, alpha=0.6)
    # Contorno da região dissolvida (preto grosso)
    gdf_regiao.boundary.plot(ax=ax, color='black', linewidth=2.0, alpha=0.8)

    cbar = plt.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label(cfg['label'], fontsize=11)
    cbar.ax.tick_params(labelsize=9)

    ax.set_title(
        f"Climatological Normal {label_str}\n{var_en} — Matas de Minas",
        fontsize=13, fontweight='bold', pad=10,
    )
    ax.set_xlabel('Longitude (°)', fontsize=11)
    ax.set_ylabel('Latitude (°)', fontsize=11)
    ax.tick_params(labelsize=9)
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    plt.tight_layout()
    plt.savefig(saida_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


def gerar_individuais(resultados, periodos, lats, lons, args,
                      gdf_mun, gdf_regiao):
    """Gera 66 mapas individuais (11 períodos × 6 variáveis)."""
    print("\n" + "=" * 60)
    print(f"4. Generating {len(VARIAVEIS) * len(periodos)} individual maps...")
    print("=" * 60)

    total = 0
    for var_nome in VARIAVEIS:
        for a0, a1 in periodos:
            lbl = periodo_label(a0, a1)
            fname = f"mapa_{var_nome}_{a0}-{a1}_MatasDeMinas.jpeg"
            fpath = os.path.join(args.saida, fname)
            plot_mapa_individual(
                resultados[var_nome][lbl], lats, lons,
                var_nome, lbl, fpath, gdf_mun, gdf_regiao,
                VARIAVEIS, VAR_EN, args.dpi,
                args.lon_min, args.lon_max, args.lat_min, args.lat_max,
            )
            total += 1
            if total % 11 == 0:
                print(f"   {total} maps generated...")

    print(f"\n   ✅ {total} individual maps generated!")
    return total


# ====================================================================
# PLOTAGEM: MAPA DE COMPARAÇÃO 3×3
# ====================================================================

def gerar_comparacao(resultados, periodos, lats, lons, args,
                     gdf_mun, gdf_regiao):
    """Gera 6 mapas de comparação 3×3 com diferenças consecutivas."""
    print("\n" + "=" * 60)
    print(f"5. Generating {len(VARIAVEIS)} comparison maps (3×3, large fonts)...")
    print("=" * 60)

    for var_nome in VARIAVEIS:
        cfg = VARIAVEIS[var_nome]
        var_en = VAR_EN[var_nome]

        # Coletar diferenças
        diffs = []
        valid_labels = []
        for i in range(1, len(COMP_LABELS)):
            la, lb = COMP_LABELS[i], COMP_LABELS[i - 1]
            pa = label_to_periodo(la, periodos)
            pb = label_to_periodo(lb, periodos)
            if pa and pb:
                la_lbl = periodo_label(*pa)
                lb_lbl = periodo_label(*pb)
                if la_lbl in resultados[var_nome] and lb_lbl in resultados[var_nome]:
                    diffs.append(resultados[var_nome][la_lbl]
                                 - resultados[var_nome][lb_lbl])
                    valid_labels.append((la, lb))

        if not diffs:
            continue

        # Limite simétrico
        all_d = np.concatenate([d.ravel() for d in diffs])
        vmax = max(abs(np.nanmin(all_d)), abs(np.nanmax(all_d)))

        # Figura GRANDE 3×3
        fig = plt.figure(figsize=(30, 28))
        gs = GridSpec(3, 3, figure=fig, hspace=0.30, wspace=0.20)

        for idx, (diff, (la, lb)) in enumerate(zip(diffs, valid_labels)):
            ax = fig.add_subplot(gs[idx // 3, idx % 3])
            extent = [lons[0] - 0.05, lons[-1] + 0.05,
                      lats[0] - 0.05, lats[-1] + 0.05]
            im = ax.imshow(diff, extent=extent, origin='lower',
                           cmap='RdBu_r', interpolation='bilinear',
                           aspect='auto', vmin=-vmax, vmax=vmax)

            gdf_mun.boundary.plot(ax=ax, color='gray', linewidth=0.3, alpha=0.4)
            gdf_regiao.boundary.plot(ax=ax, color='black', linewidth=1.8, alpha=0.7)

            ax.set_title(f"Normal {la} vs. {lb}",
                         fontsize=20, fontweight='bold', pad=10)
            ax.tick_params(labelsize=14)
            ax.set_xlabel('Longitude (°)', fontsize=15)
            ax.set_ylabel('Latitude (°)', fontsize=15)
            ax.set_xlim(args.lon_min, args.lon_max)
            ax.set_ylim(args.lat_min, args.lat_max)

        # Colorbar grande à direita
        cbar_ax = fig.add_axes([0.92, 0.12, 0.018, 0.76])
        cbar = fig.colorbar(im, cax=cbar_ax)
        cbar.set_label(f"{cfg['label']} difference", fontsize=18)
        cbar.ax.tick_params(labelsize=16)

        fig.suptitle(
            f"Variation Between Consecutive Normals — {var_en} — Matas de Minas",
            fontsize=24, fontweight='bold', y=0.97,
        )

        fname = f"comparacao_{var_nome}_normais_consecutivas.jpeg"
        fpath = os.path.join(args.saida, fname)
        plt.savefig(fpath, dpi=args.dpi, bbox_inches='tight')
        plt.close(fig)

        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        print(f"   ✓ {fname} ({size_mb:.1f} MB)")


# ====================================================================
# MAIN
# ====================================================================

def main():
    args = parse_args()
    os.makedirs(args.saida, exist_ok=True)
    os.makedirs(args.extracao, exist_ok=True)

    print("=" * 60)
    print("🌤  PesquisAI — Standard Normal Map Generator")
    print("   BR-DWGD Climatological Normals Mapping Pipeline")
    print("=" * 60)
    print(f"   Output: {args.saida}")
    print(f"   DPI:    {args.dpi}")
    print(f"   KC:     {args.kc}")
    print(f"   Idioma: {args.idioma}")

    # 1. Limites
    gdf_mun, gdf_regiao = carregar_limites(args.gpkg)

    # 2. Dados
    data_map, time_idx, lats, lons = carregar_dados(args)

    # 3. Normais
    resultados = calcular_normais(data_map, time_idx, PERIODOS_PADRAO, VARIAVEIS)

    # Liberar dados brutos
    del data_map, time_idx
    gc.collect()

    # 4. Mapas individuais
    total = gerar_individuais(resultados, PERIODOS_PADRAO, lats, lons, args,
                              gdf_mun, gdf_regiao)

    # 5. Mapas de comparação
    gerar_comparacao(resultados, PERIODOS_PADRAO, lats, lons, args,
                     gdf_mun, gdf_regiao)

    print("\n" + "=" * 60)
    print("✅ ALL DONE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   {total} individual normal maps (bilinear, English, boundaries)")
    print(f"   {len(VARIAVEIS)} comparison maps (3×3, large fonts)")
    print(f"   BH = Pr - ETo × {args.kc}")
    print(f"\n📁 Output: {args.saida}")
    print(f"\n📚 Cite: Xavier et al. (2022) doi:10.1002/joc.7731")


if __name__ == "__main__":
    main()
