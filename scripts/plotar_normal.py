#!/usr/bin/env python3
"""
plotar_normal.py
----------------
Gera mapas e gráficos das normais climatológicas do BR-DWGD.
Resolução espacial 0.1° × 0.1° é preservada na visualização.

Uso:
    python plotar_normal.py \
        --arquivo normal_pr_1991_2020.nc \
        --variavel pr \
        --escala mensal \
        --formato png

Citação:
    Xavier et al. (2022) Int. J. Climatol. doi:10.1002/joc.7731
"""

import argparse
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Nomes dos meses em português
MESES_PT = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]

# Configurações por variável
CONFIG = {
    "pr":   {"label": "Precipitação (mm)", "cmap": "Blues",      "extend": "max"},
    "Tmax": {"label": "Tmax (°C)",         "cmap": "Reds",       "extend": "both"},
    "Tmin": {"label": "Tmin (°C)",         "cmap": "RdBu_r",     "extend": "both"},
    "Rs":   {"label": "Rs (MJ/m²)",        "cmap": "YlOrRd",     "extend": "both"},
    "RH":   {"label": "Umidade Rel. (%)",  "cmap": "BrBG",       "extend": "both"},
    "u2":   {"label": "Vel. Vento (m/s)",  "cmap": "viridis",    "extend": "both"},
    "ETo":  {"label": "ETo (mm)",          "cmap": "YlGn",       "extend": "both"},
}


def plotar_painel_mensal(da: xr.DataArray, variavel: str, titulo_base: str, saida: str):
    """Cria painel 3×4 com os 12 meses da normal mensal."""
    cfg = CONFIG.get(variavel, {"label": variavel, "cmap": "viridis", "extend": "both"})

    fig, axes = plt.subplots(3, 4, figsize=(20, 14))
    axes = axes.flatten()

    vmin = float(da.min())
    vmax = float(da.max())

    for i, mes in enumerate(range(1, 13)):
        ax = axes[i]
        da_mes = da.sel(month=mes)
        im = da_mes.plot(
            ax=ax, add_colorbar=False,
            cmap=cfg["cmap"], vmin=vmin, vmax=vmax,
        )
        ax.set_title(MESES_PT[i], fontsize=11)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelsize=7)

    # Barra de cor comum
    cbar = fig.colorbar(im, ax=axes, orientation="horizontal",
                        fraction=0.03, pad=0.04, extend=cfg["extend"])
    cbar.set_label(cfg["label"], fontsize=11)

    periodo = da.attrs.get("periodo_normal", "")
    fig.suptitle(f"{titulo_base} — Normal Mensal {periodo}", fontsize=14, y=1.01)
    fig.tight_layout()
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    print(f"✓ Painel mensal salvo em: {saida}")
    plt.close()


def plotar_mapa_anual(da: xr.DataArray, variavel: str, titulo_base: str, saida: str):
    """Cria mapa único da normal anual."""
    cfg = CONFIG.get(variavel, {"label": variavel, "cmap": "viridis", "extend": "both"})

    fig, ax = plt.subplots(figsize=(10, 10))
    periodo = da.attrs.get("periodo_normal", "")
    da.plot(ax=ax, cmap=cfg["cmap"], cbar_kwargs={"label": cfg["label"], "extend": cfg["extend"]})
    ax.set_title(f"{titulo_base} — Normal Anual {periodo}", fontsize=13)
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    plt.tight_layout()
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    print(f"✓ Mapa anual salvo em: {saida}")
    plt.close()


def plotar_serie_ponto(
    ds_orig: xr.Dataset,
    variavel: str,
    lat: float,
    lon: float,
    ano_inicio: int,
    ano_fim: int,
    saida: str,
):
    """Plota série temporal mensal e normal para um ponto geográfico."""
    da = ds_orig[variavel].sel(
        latitude=lat, longitude=lon, method="nearest",
        time=slice(f"{ano_inicio}-01-01", f"{ano_fim}-12-31"),
    )
    cfg = CONFIG.get(variavel, {"label": variavel, "cmap": "viridis", "extend": "both"})

    if variavel in ("pr", "ETo"):
        mensal = da.resample(time="ME").sum()
    else:
        mensal = da.resample(time="ME").mean()

    normal = mensal.groupby("time.month").mean("time")

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Série temporal
    mensal.plot(ax=axes[0], color="steelblue", linewidth=0.8, alpha=0.7)
    axes[0].set_title(f"Série temporal mensal — Lat {lat:.2f}°, Lon {lon:.2f}°")
    axes[0].set_ylabel(cfg["label"])

    # Normal mensal
    axes[1].bar(range(1, 13), normal.values, color="steelblue", edgecolor="white")
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xticklabels(MESES_PT)
    axes[1].set_title(f"Normal climatológica mensal {ano_inicio}–{ano_fim}")
    axes[1].set_ylabel(cfg["label"])

    periodo = f"{ano_inicio}-{ano_fim}"
    fig.suptitle(f"BR-DWGD — {variavel} — Normal {periodo}", fontsize=13)
    plt.tight_layout()
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    print(f"✓ Série/normal do ponto salva em: {saida}")
    plt.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Plota normais climatológicas do BR-DWGD.")
    p.add_argument("--arquivo", required=True, help="NetCDF da normal calculada")
    p.add_argument("--variavel", required=True, help="Nome da variável no NetCDF")
    p.add_argument(
        "--escala", choices=["mensal", "anual"], default="mensal",
        help="Tipo de normal no arquivo",
    )
    p.add_argument("--formato", default="png", choices=["png", "pdf", "svg"])
    p.add_argument("--prefixo_saida", default="normal_plot")
    return p.parse_args()


def main():
    args = parse_args()
    ds = xr.open_dataset(args.arquivo)
    da = ds[args.variavel]

    saida = f"{args.prefixo_saida}.{args.formato}"
    titulo = f"BR-DWGD — {args.variavel}"

    if args.escala == "mensal":
        plotar_painel_mensal(da, args.variavel, titulo, saida)
    else:
        plotar_mapa_anual(da, args.variavel, titulo, saida)


if __name__ == "__main__":
    main()
