---
name: br-dwgd-normals
description: >
  Use this skill whenever the user needs to work with Brazilian Daily Weather Gridded Data
  (BR-DWGD) or calculate climatological normals from Brazilian meteorological gridded data.
  Triggers include any mention of BR-DWGD, normais climatológicas, normal climática,
  média de 30 anos, dados gradeados Brasil, Xavier et al. gridded data, or any request to
  calculate 30-year averages from Brazilian climate data files (NetCDF). Also triggers for
  requests to process precipitation (pr), temperature (Tmax, Tmin), solar radiation (Rs),
  relative humidity (RH), wind speed (u2), or evapotranspiration (ETo) from this dataset.
  Also triggers for requests to find the first dekad or day with accumulated precipitation
  reaching a threshold, or to extract area-weighted municipal climate series from grid data.
  Also triggers for growing degree day (GD/GDD) calculations, thermal sum accumulation,
  Antese_v2 computation, or any request to find when a temperature-based threshold is reached
  (e.g., "when does the sum of degree days reach 1980°C-dia?").
  Also triggers for computing accumulated ETo or precipitation over custom windows (e.g.,
  15-day window centered on a reference date) from 0.1°×0.1° gridded data.
  Also triggers for GENERALIZED calculations: ANY BR-DWGD variable (pr, ETo, Tmax, Tmin,
  Tmean, Rs, RH, u2) accumulated (soma) or averaged (media) over ANY period defined by two
  date columns in a spreadsheet, with pixel-area weighting for municipalities.
  Also triggers for MAP GENERATION of climatological normals — use the definitive script
  `scripts/gerar_mapa_normal_padrao.py` for bilinear-interpolated maps with municipal
  boundaries, English labels, and comparison panels (see Section 5).
  Always enforce 0.1° x 0.1° spatial resolution throughout the workflow.
---

# BR-DWGD — Normais Climatológicas & Séries Municipais

Skill para baixar, processar e calcular normais climatológicas a partir dos dados do
**Brazilian Daily Weather Gridded Data (BR-DWGD)**, e extrair séries temporais municipais
com ponderação por área de interseção pixel × município.

**Resolução espacial obrigatória: 0.1° × 0.1°** — nunca faça reamostragem ou mude essa resolução.

---

## 1. Sobre o BR-DWGD

### Formatos de dados disponíveis

| Formato | Resolução temporal | Cobertura | Tamanho aprox. | Variáveis |
|---|---|---|---|---|
| **Diário v3.2.4** ⭐ | 1 dia | **1961-01-01 a 2025-12-31** | ~2.2–2.8 GB / arquivo (3 arquivos) | **pr, Tmax, Tmin** (zip 7,7 GB) |
| **Diário v3.2.4 (outras vars)** ⭐ | 1 dia | **1961-01-01 a 2025-12-31** | **~1,1–1,4 GB / arquivo (3 arquivos)** | **ETo, u2, Rs, RH** (zip 2,1 GB) |
| **Diário v3.2.3** | 1 dia | 1961-01-01 a 2024-03-20 | ~1.2 GB / var | pr, Tmax, Tmin, Rs, RH, u2, ETo |
| **Mensal agregado v3.2.4** ⭐ | 1 mês | **1961-01 a 2025-12** | **~5 MB / var** | pr, Tmax, Tmin, **Tmean**, Rs, RH, u2, ETo |

> ⭐ **Arquivos mensais: muito mais leves (5 MB vs 2.2 GB), cobrem até 2025.**
> Prefira mensais para normais e séries anuais. Use diários para análise de eventos específicos,
> janelas sazonais precisas, ou dias exatos de atingimento de limiares.

### Arquivos diários v3.2.4 (3 arquivos por variável)

A versão v3.2.4 diária divide o período em 3 arquivos para cada variável.

**Grupo 1 — pr, Tmax, Tmin:**

| Arquivo | Período | Tamanho |
|---|---|---|
| `pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | 1961–1980 | ~2.25 GB |
| `pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | 1981–2000 | ~2.25 GB |
| `pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | 2001–2025 | ~2.80 GB |

As variáveis Tmax e Tmin seguem o mesmo padrão de nomenclatura. O download completo
(`pr_Tmax_Tmin_NetCDF_Files.zip`) tem ~7,7 GB.

**Grupo 2 — ETo, u2, Rs, RH:**

| Arquivo | Período | Tamanho |
|---|---|---|
| `ETo_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | 1961–1980 | ~1.1 GB |
| `ETo_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | 1981–2000 | ~1.1 GB |
| `ETo_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | 2001–2025 | ~1.4 GB |

As variáveis u2, Rs e RH seguem o mesmo padrão. O download completo
(`ETo_u2_RH_Rs_NetCDF_Files.zip`) tem ~2,1 GB.

> 💡 **Grupo 2 é independente!** O zip de 2,1 GB (`ETo_u2_RH_Rs`) é separado do zip de 7,7 GB
> (`pr_Tmax_Tmin`). Se precisar apenas de ETo, não precisa baixar o zip grande.

### Variáveis disponíveis

| Variável | Nome NetCDF | Unidade | Agregação (normal) | Chave script |
|---|---|---|---|---|
| Precipitação | `pr` | mm | **Soma** mensal/anual | `Pr` |
| Temperatura máxima | `Tmax` | °C | Média | `Tmax` |
| Temperatura mínima | `Tmin` | °C | Média | `Tmin` |
| **Temperatura média** | `Tmean` | °C | Média | `Tmean` |
| Radiação solar | `Rs` | MJ/m² | Média | `Rs` |
| Umidade relativa | `RH` | % | Média | `RH` |
| Velocidade vento (2m) | `u2` | m/s | Média | `u2` |
| Evapotransp. ref. | `ETo` | mm | **Soma** (já é total mensal) | `ETo` |

> `Tmean` não existe nos arquivos diários, mas **existe nos mensais**. Se só tiver Tmax e Tmin: `Tmean = (Tmax + Tmin) / 2`.

### Capitalização dos nomes

| Formato | Regra | Exemplo |
|---|---|---|
| **Mensal v3.2.4** | T maiúsculo para temperatura, minúsculo para demais | `Tmax`, `Tmin`, `Tmean`, `pr`, `ETo`, `Rs`, `RH`, `u2` |
| **Diário v3.2.3** | Todos minúsculos | `tmax`, `tmin`, `pr` |
| **Diário v3.2.4** | Minúsculos | `pr` |

### Downloads

| Tipo | Link | Acesso |
|---|---|---|---|
| Diários v3.2.4 (pr, Tmax, Tmin) | [Google Drive](https://drive.google.com/drive/folders/11-qnvwojirAtaQxSE03N0_SUrbcsz44N) — arquivo `pr_Tmax_Tmin_NetCDF_Files.zip` (7,7 GB) | gdown |
| Diários v3.2.4 (ETo, u2, Rs, RH) ⭐ | [Google Drive](https://drive.google.com/drive/folders/11-qnvwojirAtaQxSE03N0_SUrbcsz44N) — arquivo `ETo_u2_RH_Rs_NetCDF_Files.zip` (2,1 GB) | gdown + confirm (vírus scan) |
| Mensais v3.2.4 ⭐ | [Google Drive](https://drive.google.com/drive/folders/1z5pMxbQfHbMFBFosP1eIW6m5GiSiQ6t4) (~5 MB/var) | gdown |
| Diários RH v3.2.4 | [Link direto](https://drive.google.com/file/d/1meqZPSVgLGQsSrv9nGWN3CNs3gAFfaPj) (~2,2 GB zip) | gdown |
| GitHub | https://github.com/AlexandreCandidoXavier/BR-DWGD | Documentação |

> ⚠️ **Sobre o vírus scan no ETo_u2_RH_Rs_NetCDF_Files.zip (2,1 GB):**
> O Google Drive exibe um aviso de vírus scan para arquivos > 100 MB. Para contornar,
> use `requests` diretamente com UUID e confirm, ou use `gdown` e responda ao prompt
> interativo. Veja seção 2.1 para o código de contorno.

### Nomenclatura dos arquivos

| Formato | Padrão | Exemplo |
|---|---|---|
| Diário v3.2.3 | `{variavel}_BR-DWGD_UFES_UTEXAS_v_3.2.3_{inicio}_{fim}.nc` | `pr_BR-DWGD_UFES_UTEXAS_v_3.2.3_19610101_20240320.nc` |
| **Diário v3.2.4** | `{Variavel}_{inicio}_{fim}_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` | `pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc` |
| **Mensal v3.2.4** ⭐ | `{Variavel}_{ano_inicio}_{ano_fim}_BR-DWGD_monthly_v_3.2.4.nc` | `pr_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |

---

## 2. Download programático

Use `gdown` para baixar do Google Drive:

```python
import gdown, os, zipfile

# ── Arquivos mensais (v3.2.4, ~5 MB cada) ──
url_pasta = "https://drive.google.com/drive/folders/1z5pMxbQfHbMFBFosP1eIW6m5GiSiQ6t4"
gdown.download_folder(url_pasta, output="/tmp/monthly_data/", quiet=False, remaining_ok=True)

# ── Arquivos diários v3.2.4 (pr, Tmax, Tmin) ──
file_id = "1oQWHpXwFgTKNH4Fa2GwCPJ3QN1AMgNPJ"  # pr_Tmax_Tmin_NetCDF_Files.zip
zip_path = "/tmp/pr_netcdf.zip"
gdown.download(f"https://drive.google.com/uc?id={file_id}", zip_path, quiet=False)
with zipfile.ZipFile(zip_path) as z:
    z.extractall("/tmp/pr_daily/")
os.remove(zip_path)

# ── Arquivo zip grande (ex: RH diário v3.2.4) ──
file_id = "1meqZPSVgLGQsSrv9nGWN3CNs3gAFfaPj"
zip_path = "/tmp/rh_daily.zip"
gdown.download(f"https://drive.google.com/uc?id={file_id}", zip_path, quiet=False)
with zipfile.ZipFile(zip_path) as z:
    z.extractall("/tmp/daily_data/")
os.remove(zip_path)
```

> 💡 Se `gdown` não estiver instalado: `pip install gdown`.
> Para arquivos > 2 GB, usar `gdown` com `--resume`.
> Para pastas grandes, use `remaining_ok=True`.

### 2.1 Contorno de vírus scan para arquivos grandes (> 100 MB)

Para arquivos como `ETo_u2_RH_Rs_NetCDF_Files.zip` (2,1 GB) que o Google Drive bloqueia
com o aviso "Virus scan warning", use `requests` diretamente para extrair o UUID e
confirm token da página e submeter o download confirmado:

```python
import requests, re, os

file_id = "1aGdOHRT10W8oBWvE5IvmEAqJCNQOYYid"  # ETo_u2_RH_Rs_NetCDF_Files.zip
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# 1. Obter página de aviso e extrair UUID + confirm
url = f"https://drive.google.com/uc?export=download&id={file_id}"
resp = session.get(url, allow_redirects=True)

uuid = re.search(r'<input type="hidden" name="uuid" value="([^"]+)"', resp.text).group(1)
confirm = re.search(r'name="confirm"\s+value="([^"]+)"', resp.text).group(1)

# 2. Submeter download confirmado
dl_url = "https://drive.usercontent.google.com/download"
params = {"id": file_id, "export": "download", "confirm": confirm, "uuid": uuid}
resp2 = session.get(dl_url, params=params, stream=True, allow_redirects=True)

if 'text/html' not in resp2.headers.get('Content-Type', ''):
    with open("/tmp/ETo_u2_RH_Rs_NetCDF_Files.zip", 'wb') as f:
        for chunk in resp2.iter_content(chunk_size=1024*1024*10):
            if chunk:
                f.write(chunk)
    print(f"Download concluído: {os.path.getsize('/tmp/ETo_u2_RH_Rs_NetCDF_Files.zip')/1e9:.1f} GB")
else:
    print("ERRO: Download bloqueado (quota ou outro motivo)")
    print(resp2.text[:200])
```

> ⚠️ Se a página não tiver UUID ou confirm no HTML (raro), tente com `gdown` simples:
> `gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=False)`
> e responda manualmente ao prompt se solicitado.

---

## 3. Fluxos de trabalho

### 3.1 Coleta de informações do usuário

Sempre começar perguntando:

1. **Formato dos dados**: mensais (recomendado) ou diários?
2. **Objetivo**: normal climatológica, série municipal, ou dia de atingimento de limiar?
3. **Período(s)**: 30 anos OMM (1961-1990, 1971-2000, 1981-2010, 1991-2020), decadais, ou customizado?
4. **Variável(is)**: pr, Tmax, Tmin, Tmean, Rs, RH, u2, ETo?
5. **Escala temporal**: mensal (12 valores), anual (1 valor), ou diária (séries)?
6. **Domínio espacial**: todo Brasil, bbox, ou municípios específicos?
7. **Formato de saída**: CSV, NetCDF, GeoTIFF, mapa, ou coluna em planilha existente?

### 3.2 Abrindo dados mensais

```python
import xarray as xr, numpy as np, pandas as pd

# Dados mensais — cabem inteiros na RAM (~5 MB)
ds = xr.open_dataset("/tmp/monthly_data/pr_1961_2025_BR-DWGD_monthly_v_3.2.4.nc")

# Verificar resolução
lat_res = abs(float(ds.latitude.diff("latitude").mean()))
lon_res = abs(float(ds.longitude.diff("longitude").mean()))
assert abs(lat_res - 0.1) < 1e-4 and abs(lon_res - 0.1) < 1e-4
print(f"Resolução: {lat_res:.2f}° × {lon_res:.2f}° ✓")

# Estrutura: (time: 780 meses, latitude: N, longitude: M)
```

### 3.3 Abrindo dados diários v3.2.4

```python
import xarray as xr

# Dados diários v3.2.4 — usar chunks para memória
arquivos = [
    "/tmp/pr_daily/pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "/tmp/pr_daily/pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "/tmp/pr_daily/pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
]

# Carregar como lazy, depois fazer subset e load()
ds_list = []
for nc_path in arquivos:
    ds = xr.open_dataset(nc_path, chunks={"time": 365})
    # Subset espacial ANTES de carregar em memória
    ds_sub = ds.sel(latitude=slice(-21.5, -19.2), longitude=slice(-43.3, -41.1))
    ds_sub = ds_sub.load()  # só carrega o subset
    ds_list.append(ds_sub)

ds_all = xr.concat(ds_list, dim="time")
```

> ⚠️ **Atenção para a ordenação da latitude nos diários v3.2.4:**
> Diferente da v3.2.3, a **v3.2.4 tem latitude crescente** (de sul para norte:
> de -34° para +5°). Portanto, use `slice(lat_min, lat_max)` e não o inverso.
>
> | Versão | Ordem da latitude | slice correto |
> |---|---|---|
> | v3.2.3 | Decrescente (5 → -34) | `slice(lat_max, lat_min)` |
> | **v3.2.4** | **Crescente (-34 → 5)** | `slice(lat_min, lat_max)` |
>
> Verifique sempre com `print(ds.latitude.values[:3], ds.latitude.values[-3:])`.

### 3.4 Recorte espacial por bbox

```python
# v3.2.4: latitude crescente
ds_sub = ds.sel(
    latitude=slice(lat_min, lat_max),
    longitude=slice(lon_min, lon_max)
)
```

### 3.5 Cálculo de normais para cada variável

**Regra de ouro:**

| Tipo | Variáveis | Agregação temporal |
|---|---|---|
| **Acumuladas (soma)** | `pr`, `ETo` | Soma mensal → média entre anos |
| **Médias** | `Tmax`, `Tmin`, `Tmean`, `Rs`, `RH`, `u2` | Média mensal → média entre anos |

```python
def calcular_normal_anual(da, ano_ini, ano_fim, variavel):
    """Retorna array 2D (lat, lon) com a média anual do período."""
    dados = da.sel(time=slice(f"{ano_ini}-01", f"{ano_fim}-12"))
    anos = pd.DatetimeIndex(dados.time.values).year
    anos_unicos = np.unique(anos)

    if variavel in ("pr", "ETo"):
        # Soma anual → média entre anos
        anuais = np.array([
            dados.values[anos == yr].sum(axis=0) for yr in anos_unicos
        ])
    else:
        # Média anual → média entre anos
        anuais = np.array([
            dados.values[anos == yr].mean(axis=0) for yr in anos_unicos
        ])
    return np.mean(anuais, axis=0)
```

> ⚠️ **ETo mensal** já é o total acumulado do mês (mm/mês). Basta somar os meses para obter o anual.
> Se estiver usando dados **diários** de ETo (mm/dia), multiplique por dias do mês.

### 3.6 Extração para municípios com ponderação por área

Use `geopandas` + interseção geométrica para ponderar cada pixel pela área de interseção com o polígono do município:

```python
import geopandas as gpd
from shapely.geometry import box

def area_weighted_mean(grid_2d, lats, lons, municipio_polygon):
    """
    grid_2d:  (lat, lon) com valores climáticos
    lats, lons: vetores 1D
    municipio_polygon: shapely polygon em EPSG:4674
    """
    # Criar polígono para cada pixel
    pixel_polys = []
    pixel_vals = []
    for i in range(len(lats) - 1):
        for j in range(len(lons) - 1):
            cell = box(lons[j], lats[i+1], lons[j+1], lats[i])
            if cell.intersects(municipio_polygon):
                pixel_polys.append(cell)
                pixel_vals.append(grid_2d[i, j])

    if not pixel_polys:
        return np.nan

    # Calcular área de interseção (projetar para planar)
    gdf_pixels = gpd.GeoDataFrame(
        {"value": pixel_vals, "geometry": pixel_polys}, crs="EPSG:4674"
    ).to_crs("EPSG:5880")  # Policônica Brasil para áreas

    gdf_mun = gpd.GeoDataFrame(
        {"geometry": [municipio_polygon]}, crs="EPSG:4674"
    ).to_crs("EPSG:5880")

    areas = gdf_pixels.intersection(gdf_mun.geometry.iloc[0]).area
    total = areas.sum()
    if total == 0:
        return np.nan
    return np.average(gdf_pixels["value"], weights=areas)
```

> 💡 Para validação: a soma dos pesos de todos os pixels de um município deve ser ~1.
> 💡 **Otimização**: pré-calcule os pesos uma vez e reutilize para todos os anos, em vez de
> recalcular as intersecções a cada ano.

### 3.7 Cálculo de limiar de precipitação acumulada (Dec_abril_16mm)

Este fluxo calcula o primeiro dia a partir de 1º de abril em que a precipitação acumulada
atinge um limiar (padrão: 16 mm) para cada município-ano em uma planilha Excel.

```python
def primeira_data_acumulado_16mm(pr_municipio, time_index, ano, limiar=16.0):
    """
    pr_municipio: array 1D de precipitação diária (série temporal completa)
    time_index: pd.DatetimeIndex correspondente
    ano: ano de interesse
    limiar: mm acumulados para disparo

    Retorna dict com status e data encontrada
    """
    data_ini = pd.Timestamp(f"{ano}-04-01")
    data_fim = pd.Timestamp(f"{ano}-12-31")

    mask = (time_index >= data_ini) & (time_index <= data_fim)
    idx = np.where(mask)[0]

    if len(idx) == 0:
        return {"status": "SEM_DADOS"}

    pr = pr_municipio[idx]
    pr_acum = np.cumsum(pr)
    alvo = np.where(pr_acum >= limiar)[0]

    if len(alvo) == 0:
        return {"status": "NAO_ATINGIU"}

    return {
        "status": "ATINGIU",
        "data": time_index[idx[alvo[0]]],
        "dias_desde_abril": alvo[0],
        "pr_acum": float(pr_acum[alvo[0]]),
    }
```

**Pipeline completo para planilha Excel:**

```python
# 1. Para cada município: calcular pesos de área UMA VEZ
pesos_mun = {}
for mun_nome, cod_str in mun_to_cod.items():
    poly = gdf.loc[cod_str, "geometry"]
    weight_map, _ = compute_pixel_weights(poly, lats, lons)
    pesos_mun[mun_nome] = weight_map

# 2. Para cada município: extrair série temporal completa
for mun_nome, weight_map in pesos_mun.items():
    pr_mun = np.zeros(len(times), dtype=np.float64)
    for (i, j), w in weight_map.items():
        pr_mun += pr_data[:, i, j] * w

    # 3. Para cada ano deste município: calcular limiar
    for ano in anos_do_municipio:
        res = primeira_data_acumulado_16mm(pr_mun, time_idx, ano)
        # Escrever na planilha
```

> ⚠️ **Dados diários são volumosos!** Para evitar problemas de memória:
> - Sempre faça o **subset espacial** (bbox da região de interesse) antes de carregar
> - Use `chunks={"time": 365}` no `open_dataset`
> - O subset da região de café de MG (~25 × 24 pixels) cabe em ~114 MB para ~23.700 dias

### 3.8 Cálculo de Graus-Dia (Soma Térmica) — Antese_v2

Este fluxo calcula a data em que o somatório de graus-dia (GD) atinge um limiar
pré-definido a partir de uma data inicial (ex: `Dec_abril_16mm`), usando dados diários
de Tmax e Tmin do BR-DWGD.

**Aplicação agrometeorológica:** Determinação da data provável de florescimento (antese)
do café com base na soma térmica acumulada, comumente usando o limiar de 1980°C-dia
e temperatura base de 8,5°C.

#### 3.8.1 Definição de Grau-Dia

$$ GD_{diário} = \frac{Tmax + Tmin}{2} - T_{base} $$

Onde:
- \( T_{base} \) = temperatura base da cultura (ex: 8,5°C para café arábica)
- Se \( GD < 0 \), assume-se \( GD = 0 \) (não acumula valores negativos)

**Exemplo:** Se Tmax = 28°C e Tmin = 17°C:
$$ T_{med} = \frac{28 + 17}{2} = 22,5°C $$
$$ GD = 22,5 - 8,5 = 14°C $$

#### 3.8.2 Função de Cálculo Diário

```python
def calcular_grau_dia_diario(tmax_mun, tmin_mun, base_temp=8.5):
    """
    Calcula graus-dia diários para um município.
    
    Args:
        tmax_mun: array 1D de Tmax diária
        tmin_mun: array 1D de Tmin diária
        base_temp: temperatura base (°C)
    
    Returns:
        gd: array 1D de graus-dia diários (valores >= 0)
    """
    tmed = (tmax_mun + tmin_mun) / 2.0
    gd = tmed - base_temp
    gd = np.maximum(gd, 0.0)  # não acumular valores negativos
    return gd
```

#### 3.8.3 Data de Atingimento da Soma Térmica

```python
def encontrar_data_atinge_soma(gd_array, time_idx, data_inicio, soma_alvo=1980.0):
    """
    Encontra a primeira data a partir de data_inicio em que a soma
    acumulada de graus-dia atinge soma_alvo.
    
    Args:
        gd_array: array 1D de graus-dia diários
        time_idx: pd.DatetimeIndex
        data_inicio: pd.Timestamp da data de partida
        soma_alvo: valor alvo da soma térmica (°C-dia)
    
    Returns:
        data_atinge: pd.Timestamp ou None
        soma_atingiu: float (soma acumulada na data encontrada)
        dias_corridos: int (dias desde data_inicio)
    """
    mask_inicio = time_idx >= data_inicio
    idx_inicio = np.where(mask_inicio)[0]
    
    if len(idx_inicio) == 0:
        return None, 0, 0
    
    i0 = idx_inicio[0]
    gd_periodo = gd_array[i0:]
    soma_acum = np.cumsum(gd_periodo)
    
    idx_alvo = np.where(soma_acum >= soma_alvo)[0]
    
    if len(idx_alvo) == 0:
        return None, float(soma_acum[-1]), len(gd_periodo)
    
    i_alvo = idx_alvo[0]
    data_atinge = time_idx[i0 + i_alvo]
    return data_atinge, float(soma_acum[i_alvo]), i_alvo
```

#### 3.8.4 Pipeline Completo para Planilha Excel

O pipeline combina a ponderação por área (seção 3.6) com o cálculo de graus-dia:

```python
# 1. Carregar Tmax e Tmin diários com subset espacial
arquivos_tmax = [
    "Tmax_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "Tmax_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "Tmax_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
]
arquivos_tmin = [
    "Tmin_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "Tmin_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "Tmin_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
]

# 2. Subset espacial e concatenação (mesmo padrão da seção 3.7)
ds_tmax = xr.concat([xr.open_dataset(f, chunks={"time": 365})
                      .sel(latitude=slice(LAT_MIN, LAT_MAX),
                           longitude=slice(LON_MIN, LON_MAX)).load()
                     for f in arquivos_tmax], dim="time")
ds_tmin = xr.concat([xr.open_dataset(f, chunks={"time": 365})
                      .sel(latitude=slice(LAT_MIN, LAT_MAX),
                           longitude=slice(LON_MIN, LON_MAX)).load()
                     for f in arquivos_tmin], dim="time")

tmax_all = ds_tmax["Tmax"].values  # (time, lat, lon)
tmin_all = ds_tmin["Tmin"].values
time_idx = pd.DatetimeIndex(ds_tmax.time.values)

# 3. Para cada município: extrair série Tmax/Tmin ponderada
for mun_nome, weight_map in pesos_mun.items():
    tmax_mun = np.zeros(len(time_idx), dtype=np.float64)
    tmin_mun = np.zeros(len(time_idx), dtype=np.float64)
    for (i, j), w in weight_map.items():
        tmax_mun += tmax_all[:, i, j] * w
        tmin_mun += tmin_all[:, i, j] * w
    
    # Calcular GD para toda a série
    gd_mun = calcular_grau_dia_diario(tmax_mun, tmin_mun)
    
    # Para cada ano: encontrar data de atingimento
    for ano in anos_do_municipio:
        data_inicio = pd.Timestamp(f"{ano-1}-04-01")  # ou data do Dec_abril_16mm
        data_atinge, soma, dias = encontrar_data_atinge_soma(
            gd_mun, time_idx, data_inicio, soma_alvo=1980.0
        )
```

> ⚠️ **A data de partida** pode ser fixa (ex: 1º de abril) ou variável por município-ano
> (ex: coluna `Dec_abril_16mm` da planilha). O script `calcular_antese_v2.py` usa a
> data da coluna `Dec_abril_16mm` como referência inicial.

### 3.9 Cálculo de variáveis acumuladas em janela centrada em data de referência (ex: Antese)

Este fluxo calcula o somatório de uma variável (ex: Pr, ETo) em uma janela de N dias
centrada em uma data de referência para cada município-ano em uma planilha.

**Aplicação típica:** Precipitação acumulada (`Pr_antese_mm`) e evapotranspiração
acumulada (`ETo_antese_mm`) durante o período de antese do café: 5 dias antes +
dia da antese + 10 dias depois = **15 dias**.

#### 3.9.1 Download dos dados diários

Para Pr: baixar `pr_Tmax_Tmin_NetCDF_Files.zip` (7,7 GB — pode ter quota excedida).
Para ETo/u2/Rs/RH: baixar `ETo_u2_RH_Rs_NetCDF_Files.zip` (2,1 GB — usar seção 2.1).

```python
# Extrair apenas os arquivos da variável desejada do zip
import zipfile, os

# Exemplo: baixar e extrair ETo do zip
zip_path = "/tmp/ETo_u2_RH_Rs_NetCDF_Files.zip"
output_dir = "/tmp/br-dwgd-daily/"

with zipfile.ZipFile(zip_path) as z:
    for name in z.namelist():
        if name.startswith("ETo_"):  # ou "pr_", "RH_", etc.
            z.extract(name, output_dir)
os.remove(zip_path)  # liberar espaço
```

#### 3.9.2 Pré-computação dos pesos de área

Os pesos de interseção pixel × município devem ser calculados **uma única vez**
e reutilizados para todos os anos e todas as variáveis:

```python
import geopandas as gpd
from shapely.geometry import box
import xarray as xr, numpy as np

# Carregar um arquivo NetCDF para obter as coordenadas da grade
ds_ref = xr.open_dataset("/tmp/br-dwgd-daily/ETo_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc")
lats = ds_ref.latitude.values
lons = ds_ref.longitude.values

# Definir bbox da região de interesse para reduzir o grid
lat_min, lat_max = -21.8, -19.0
lon_min, lon_max = -43.8, -41.0

# Subset das coordenadas
lat_region = lats[(lats >= lat_min) & (lats <= lat_max)]
lon_region = lons[(lons >= lon_min) & (lons <= lon_max)]

# Criar grid cells da região
grid_cells = []
for i, lat in enumerate(lat_region):
    for j, lon in enumerate(lon_region):
        grid_cells.append({
            'lat_idx': i, 'lon_idx': j,
            'geometry': box(lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05)
        })
grid_gdf = gpd.GeoDataFrame(grid_cells, crs="EPSG:4674")

# Carregar municípios
mun = gpd.read_file("/path/to/MUN_MATAS.gpkg")
mun = mun.to_crs("EPSG:4674")

# Spatial join e cálculo das áreas de interseção
sjoin = gpd.sjoin(mun, grid_gdf, how='inner', predicate='intersects')

weights = {}
for left_idx in sjoin.index.unique():
    rows = sjoin.loc[[left_idx]]
    mun_geom = mun.geometry.iloc[left_idx]
    total_area = mun_geom.area
    
    cells = []
    for _, row in rows.iterrows():
        cell_geom = grid_gdf.geometry.iloc[row['index_right']]
        area = mun_geom.intersection(cell_geom).area
        if area > 0:
            cells.append({
                'lat_idx': int(row['lat_idx']),
                'lon_idx': int(row['lon_idx']),
                'weight': area / total_area,
            })
    
    if cells:
        weights[left_idx] = cells

print(f"Pesos calculados para {len(weights)} municípios")
# A soma dos pesos para cada município deve ser ~1.0
```

#### 3.9.3 Extração da série temporal diária ponderada

```python
# Carregar os 3 arquivos NetCDF, subset na região, extrair séries
files = [
    "/tmp/br-dwgd-daily/VAR_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "/tmp/br-dwgd-daily/VAR_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "/tmp/br-dwgd-daily/VAR_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
]

all_data = []
for nc_path in files:
    with xr.open_dataset(nc_path) as ds:
        # Subset espacial
        ds_sub = ds.sel(latitude=slice(lat_region[0], lat_region[-1]),
                        longitude=slice(lon_region[0], lon_region[-1]))
        var_name = list(ds_sub.data_vars)[0]
        data = ds_sub[var_name].values  # (time, lat, lon)
    
    n_time = data.shape[0]
    mun_data = np.full((len(weights), n_time), np.nan, dtype=np.float32)
    
    for idx_mun, cells in weights.items():
        vals = np.zeros(n_time, dtype=np.float64)
        for cell in cells:
            vals += data[:, cell['lat_idx'], cell['lon_idx']] * cell['weight']
        mun_data[idx_mun] = vals.astype(np.float32)
    
    all_data.append(mun_data)

# Concatenar os 3 períodos
var_full = np.concatenate(all_data, axis=1)  # (n_mun, 23741)
print(f"Série temporal: {var_full.shape}")
print(f"Período: 1961-01-01 a 2025-12-31")
```

> 💡 Para **ETo**, os valores diários estão em mm/dia. O somatório sobre a janela
> de 15 dias dá o total em mm.
> Para **Pr**, os valores diários estão em mm/dia. O somatório sobre a janela dá
> a precipitação total acumulada em mm.

#### 3.9.4 Cálculo da janela centrada na data de referência

```python
from datetime import datetime, timedelta
import pandas as pd

# Mapa: data → índice no array (1961-01-01 = índice 0)
start = datetime(1961, 1, 1)
dates = [start + timedelta(days=i) for i in range(var_full.shape[1])]
date_to_idx = {d.strftime('%Y-%m-%d'): i for i, d in enumerate(dates)}

# Mapa: código IBGE → índice do município (ordem do GeoPackage)
ibge_to_mun_idx = {str(code): i for i, code in enumerate(mun['CD_MUN'])}

# Para cada linha da planilha
resultados = np.full(len(df), np.nan)

for i, row in df.iterrows():
    ibge = str(row['Código IBGE'])
    antese = pd.to_datetime(row['Antese'])
    
    if ibge not in ibge_to_mun_idx:
        continue
    
    mun_idx = ibge_to_mun_idx[ibge]
    date_str = antese.strftime('%Y-%m-%d')
    
    if date_str not in date_to_idx:
        continue
    
    idx = date_to_idx[date_str]
    
    # Janela: N dias antes + dia + M dias depois
    N_ANTES = 5
    M_DEPOIS = 10
    start_idx = max(0, idx - N_ANTES)
    end_idx = min(var_full.shape[1] - 1, idx + M_DEPOIS)
    
    soma = float(var_full[mun_idx, start_idx:end_idx + 1].sum())
    resultados[i] = soma

print(f"Calculados: {np.sum(~np.isnan(resultados))}/{len(df)} registros")
```

#### 3.9.5 Parâmetros configuráveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| Dias antes | 5 | Quantos dias antes da referência incluir |
| Dias depois | 10 | Quantos dias depois da referência incluir |
| Variável | ETo | Nome da variável no NetCDF |
| Coluna data | Antese | Coluna com a data de referência |
| Coluna alvo | ETo_antese_mm | Coluna para escrita do resultado |

#### 3.9.6 Pipeline completo para planilha Excel

```python
# 1. Baixar e extrair ETo ou Pr (seções 2.0/2.1)
# 2. Calcular pesos de área (seção 3.9.2)
# 3. Carregar dados diários e extrair séries municipais (seção 3.9.3)
# 4. Para cada linha: calcular soma na janela (seção 3.9.4)
# 5. Escrever na planilha
from openpyxl import load_workbook

wb = load_workbook(xlsx_path)
ws = wb["DELTA PRODUTIVIDADE (brutos)"]

# Encontrar coluna alvo
col_map = {cell.value: cell.column for cell in ws[1]}
col_alvo = col_map.get('ETo_antese_mm')  # ou 'Pr_antese_mm'

for i, val in enumerate(resultados):
    ws.cell(row=i+2, column=col_alvo, value=float(val))

wb.save(xlsx_path)
print(f"{len(resultados)} valores escritos em {xlsx_path}")
```

> ⚠️ **Quota excedida no Google Drive:** O arquivo `pr_Tmax_Tmin_NetCDF_Files.zip`
> (7,7 GB) pode ficar indisponível por ~24h se muitos downloads forem feitos.
> O arquivo `ETo_u2_RH_Rs_NetCDF_Files.zip` (2,1 GB) geralmente está disponível
> (apenas vírus scan warning, contornável — seção 2.1).
>
> Se ambos os downloads estiverem bloqueados, **pergunte ao pesquisador no terminal**
> se ele deseja usar uma aproximação alternativa (ex: interpolação por estações, dados
> mensais como referência, ou aguardar o reset da cota). Nunca decida autonomamente
> por um método substituto sem consultar o pesquisador.

### 3.10 Janelas sazonais específicas (ex: 15-set a 15-nov para cafeicultura)

Dados mensais não permitem janelas de 15 dias, mas a ponderação por mês funciona bem:

```python
# Peso: Set=0.25, Out=0.50, Nov=0.25
rh_sep = da_rh.sel(time=da_rh.time.dt.month.isin([9]))
rh_oct = da_rh.sel(time=da_rh.time.dt.month.isin([10]))
rh_nov = da_rh.sel(time=da_rh.time.dt.month.isin([11]))
rh_window = 0.25 * rh_sep + 0.50 * rh_oct + 0.25 * rh_nov
```

Se precisar de janelas precisas (ex: 15-set a 15-nov), use dados diários:

```python
# Dados diários
rh_daily = xr.open_dataset("/tmp/daily_data/RH_*.nc", chunks={"time": 365})
rh_window = rh_daily.sel(time=rh_daily.time.dt.month.isin([9, 10, 11]))
# Filtrar dias: 15-set a 15-nov
rh_window = rh_window.where(
    (rh_window.time.dt.month > 9) |
    (rh_window.time.dt.month < 11) |
    ((rh_window.time.dt.month == 9) & (rh_window.time.dt.dayofyear >= 258)) |
    ((rh_window.time.dt.month == 11) & (rh_window.time.dt.dayofyear <= 319))
)
rh_window_mean = rh_window.mean(dim="time")
```

---

### 3.11 ★ Generalizado: qualquer variável, qualquer período

A **função mais poderosa** desta skill permite calcular **qualquer variável do BR-DWGD**,
com **qualquer agregação** (soma ou média), para **qualquer período** definido por
duas colunas de data em uma planilha Excel.

Em vez de um script específico para cada combinação (Pr_160d, ETo_160d, Pr_MF, ETo_MF, etc.),
use um **único script** parametrizável:

```bash
python scripts/calcular_variavel_periodo.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel pr \
    --coluna_ini "Antese" \
    --coluna_fim "160dias_antese" \
    --coluna_alvo "Pr_160d_mm" \
    --agregacao soma
```

**O que o script faz automaticamente:**
1. Detecta se os dados são v3.2.3 (1 arquivo) ou v3.2.4 (3 arquivos)
2. Identifica a ordenação da latitude (crescente ou decrescente)
3. Calcula a bbox expandida dos municípios e faz subset espacial
4. Calcula pesos de área pixel × município (uma única vez)
5. Extrai séries ponderadas para todos os municípios
6. Para cada linha: soma ou média dos valores entre `coluna_ini` e `coluna_fim`
7. Escreve na `coluna_alvo` sem alterar nada mais na planilha

**Regra de agregação automática:**
- `pr` e `ETo` → `soma` (acumulado no período)
- `Tmax`, `Tmin`, `Tmean`, `Rs`, `RH`, `u2` → `media` (média no período)

O pesquisador pode forçar qualquer agregação com `--agregacao soma` ou `--agregacao media`.

Consulte a seção 4.4 para documentação completa, exemplos e parâmetros.

---

## 4. Scripts inclusos

| Script | Função |
|---|---|---|
| `scripts/calcular_normal.py` | Calcula normais de 30 anos (CLI) — dados diários |
| `scripts/extrair_municipios.py` | Extrai séries municipais com ponderação por área — dados mensais |
| `scripts/processar_dec_abril_16mm.py` | Calcula 1º dia com precipitação acumulada ≥ limiar a partir de abril — dados diários |
| **`scripts/calcular_antese_v2.py`** ⭐ | **Calcula data de atingimento de soma térmica (graus-dia) — Tmax/Tmin diários** |
| **`scripts/calcular_janela_acumulo.py`** 🆕 | **Calcula soma de ETo/Pr em janela centrada em data de referência (ex: Antese) — dados diários** |
| **`scripts/calcular_variavel_periodo.py`** 🚀 | **★ GENERALIZADO: calcula qualquer variável BR-DWGD (soma ou média) para qualquer período definido por colunas de data na planilha — dados diários e mensais** |
| `scripts/plotar_normal.py` | Gera mapas básicos (pcolormesh, português) |
| **`scripts/gerar_mapa_normal_padrao.py`** ⭐ | **★ GERAÇÃO DEFINITIVA: bilinear, hierarquia de limites, inglês, 66 individuais + 6 comparação 3×3, BH = Pr − ETo × Kc** |

### 4.1 Script: `processar_dec_abril_16mm.py`

**Uso típico:**
```bash
python scripts/processar_dec_abril_16mm.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --sheet "DELTA PRODUTIVIDADE (brutos)" \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/pr_daily \
    --coluna_mun "Município" \
    --coluna_ano "Ano" \
    --coluna_cod "Código IBGE" \
    --coluna_alvo "Dec_abril_16mm" \
    --limiar 16.0
```

**Funcionamento:**
1. Lê a planilha Excel com municípios, anos e códigos IBGE
2. Carrega geometrias municipais de um GeoPackage
3. Abre os dados diários de precipitação BR-DWGD v3.2.4 (subset na bbox)
4. Calcula os pesos de área para cada município (uma única vez)
5. Para cada município-ano, encontra o 1º dia a partir de 1º de abril em que a
   precipitação acumulada ≥ limiar (padrão: 16 mm)
6. Escreve a data (DD/MM/YYYY) na coluna alvo da planilha

**Dependências:** `xarray netcdf4 geopandas openpyxl shapely numpy pandas`

### 4.2 Script: `calcular_antese_v2.py` ⭐

**Uso típico — linha de comando:**
```bash
python scripts/calcular_antese_v2.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --sheet "DELTA PRODUTIVIDADE (brutos)" \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --coluna_mun "Município" \
    --coluna_ano "Ano" \
    --coluna_cod "Código IBGE" \
    --coluna_dec "Dec_abril_16mm" \
    --coluna_antese_v2 "Antese_v2" \
    --soma_alvo 1980.0 \
    --base_temp 8.5
```

**O que faz:**
1. Lê planilha Excel com municípios, anos, códigos IBGE e data de partida (`Dec_abril_16mm`)
2. Carrega geometrias municipais de um GeoPackage (EPSG:4674)
3. Baixa e processa **Tmax e Tmin diários** do BR-DWGD v3.2.4 (subset na bbox da região)
4. Calcula pesos de área para cada município (pixel 0,1° × polígono municipal)
5. Extrai séries temporais ponderadas de Tmax e Tmin para cada município
6. Calcula graus-dia diários: `GD = (Tmax + Tmin) / 2 - Tbase` (GD < 0 → 0)
7. Para cada município-ano, a partir da data `Dec_abril_16mm`, acumula GD até atingir `soma_alvo`
8. Escreve a data de atingimento (`YYYY-MM-DD`) na coluna `Antese_v2`

**Pipeline completo (passo a passo):**

```
Planilha + GeoPackage → Pesos de área (única vez)
    ↓
BR-DWGD Tmax/Tmin → Subset espacial → Carregamento lazy
    ↓
Para cada município: série ponderada de Tmax e Tmin
    ↓
Cálculo de GD diário para todo o período
    ↓
Para cada município-ano:
    Data partida = Dec_abril_16mm
    Soma acumulada de GD
    Data de atingimento = 1º dia com soma ≥ 1980°C-dia
    ↓
Escreve na coluna Antese_v2
```

**Parâmetros chave:**

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--soma_alvo` | 1980.0 | Soma térmica alvo (°C-dia) |
| `--base_temp` | 8.5 | Temperatura base da cultura (°C) |
| `--coluna_dec` | `Dec_abril_16mm` | Coluna com data de partida |
| `--coluna_antese_v2` | `Antese_v2` | Coluna alvo para escrita |

**Comportamento com GD negativo:**
Valores de GD negativos são **zerados** (não acumulam), impedindo que dias frios
"consumam" o saldo térmico já acumulado. Isso é consistente com a definição
agronômica de graus-dia.

**Como usar via Python (importação):**
```python
from calcular_antese_v2 import calcular_grau_dia_diario, encontrar_data_atinge_soma

gd = calcular_grau_dia_diario(tmax_array, tmin_array, base_temp=8.5)
data, soma, dias = encontrar_data_atinge_soma(gd, time_idx, data_inicio, soma_alvo=1980.0)
print(f"Antese prevista: {data.strftime('%Y-%m-%d')} ({dias} dias, {soma:.0f}°C-dia)")
```

**Dependências:** `xarray netcdf4 geopandas openpyxl shapely numpy pandas`

> 💡 **Performance:** Para 64 municípios e ~23.700 dias, o processamento leva
> ~75 segundos em 2 vCPUs. O subset da região das Matas de Minas (~24×23 pixels)
> consome ~210 MB na RAM.

### 4.3 Script: `calcular_janela_acumulo.py` 🆕

**Uso típico — linha de comando:**
```bash
python scripts/calcular_janela_acumulo.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --sheet "DELTA PRODUTIVIDADE (brutos)" \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel ETo \
    --coluna_mun "Município" \
    --coluna_cod "Código IBGE" \
    --coluna_ref "Antese" \
    --coluna_alvo "ETo_antese_mm" \
    --dias_antes 5 \
    --dias_depois 10
```

**O que faz:**
1. Lê planilha Excel com municípios, anos, códigos IBGE e data de referência
2. Carrega geometrias municipais de um GeoPackage (EPSG:4674)
3. Baixa/processa os dados diários da variável escolhida (ETo ou Pr) do BR-DWGD v3.2.4
4. Calcula pesos de área para cada município (pixel 0,1° × polígono municipal) — **uma única vez**
5. Extrai séries temporais ponderadas para cada município
6. Para cada registro: soma os valores na janela [`data_ref` - `dias_antes`, `data_ref` + `dias_depois`]
7. Escreve o somatório na coluna alvo da planilha

**Parâmetros chave:**

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--variavel` | ETo | Variável a processar: `ETo`, `pr`, `Rs`, `RH`, `u2` |
| `--dias_antes` | 5 | Dias antes da data de referência |
| `--dias_depois` | 10 | Dias depois da data de referência |
| `--coluna_ref` | Antese | Coluna com a data de referência |
| `--coluna_alvo` | ETo_antese_mm | Coluna alvo para escrita |

**Dependências:** `xarray netcdf4 geopandas openpyxl shapely numpy pandas`

### 4.4 Script: `calcular_variavel_periodo.py` 🚀 — **GENERALIZADO**

Este é o script **mais flexível** da skill. Ele generaliza todo o pipeline de extração e cálculo para **qualquer variável do BR-DWGD**, para **qualquer período** definido por duas colunas de data em uma planilha Excel.

**Filosofia:** O pesquisador pode definir QUAL variável, QUAL período e QUAL agregação — o script cuida de todo o resto (download, subset, pesos de área, extração municipal, cálculo e escrita).

**Uso típico — linha de comando:**
```bash
python scripts/calcular_variavel_periodo.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --sheet "DELTA PRODUTIVIDADE (brutos)" \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel pr \
    --coluna_mun "Município" \
    --coluna_cod "Código IBGE" \
    --coluna_ini "Antese" \
    --coluna_fim "160dias_antese" \
    --coluna_alvo "Pr_160d_mm" \
    --agregacao soma
```

#### Variáveis suportadas

| Variável | Código `--variavel` | Unidade | Agregação padrão | Agregação alternativa |
|---|---|---|---|---|
| Precipitação | `pr` | mm | `soma` | `media` |
| Evapotransp. ref. | `ETo` | mm | `soma` | `media` |
| Temp. máxima | `Tmax` | °C | `media` | `soma` |
| Temp. mínima | `Tmin` | °C | `media` | `soma` |
| Temp. média | `Tmean` | °C | `media` | `soma` |
| Radiação solar | `Rs` | MJ/m² | `media` | `soma` |
| Umidade relativa | `RH` | % | `media` | `soma` |
| Veloc. vento 2m | `u2` | m/s | `media` | `soma` |

#### Opções disponíveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--planilha` | (obrigatório) | Caminho para planilha Excel (.xlsx) |
| `--sheet` | (auto-detecta) | Nome da sheet (se única, detecta automaticamente) |
| `--gpkg` | (obrigatório) | GeoPackage dos municípios |
| `--dir_dados` | (obrigatório) | Diretório com arquivos NetCDF (v3.2.4 ou v3.2.3) |
| `--variavel` | (obrigatório) | Nome da variável (pr, ETo, Tmax, Tmin, Tmean, Rs, RH, u2) |
| `--coluna_mun` | `Município` | Coluna com nome do município |
| `--coluna_cod` | `Código IBGE` | Coluna com código IBGE (deve bater com CD_MUN do GPKG) |
| `--coluna_ini` | (obrigatório) | Coluna com **data inicial** do período |
| `--coluna_fim` | (obrigatório) | Coluna com **data final** do período |
| `--coluna_alvo` | (obrigatório) | Coluna onde escrever o resultado |
| `--agregacao` | auto | `soma` (acumulado) ou `media` (média). Padrão inteligente |
| `--buffer` | 0.5 | Buffer (graus) ao redor dos municípios para bbox |
| `--formato` | `diario` | `diario` ou `mensal` |

#### Agregação inteligente (auto-detect)

Se `--agregacao` não for informado:
- **`pr` e `ETo`** → usam `soma` (são variáveis de acumulação)
- **Demais variáveis** (Tmax, Tmin, Tmean, Rs, RH, u2) → usam `media`

Se o pesquisador quiser, por exemplo, a **precipitação média diária** no período em vez do total acumulado, basta passar `--agregacao media`.

#### Formato de data aceito

O script aceita datas nos formatos:
- `YYYY-MM-DD` (ex: `1974-10-06`)
- `YYYY-MM-DD HH:MM:SS` (ex: `1974-10-06 00:00:00`)
- `DD/MM/YYYY` (ex: `06/10/1974`)

#### Exemplos de uso

```bash
# 1. Precipitação acumulada entre Antese e MF
python scripts/calcular_variavel_periodo.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --sheet "DELTA PRODUTIVIDADE (brutos)" \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel pr \
    --coluna_cod "Código IBGE" \
    --coluna_ini "Antese" \
    --coluna_fim "MF" \
    --coluna_alvo "Pr_MF_mm"

# 2. Temperatura máxima média no período vegetative
python scripts/calcular_variavel_periodo.py \
    --planilha dados_cafe.xlsx \
    --gpkg municipios.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel Tmax \
    --coluna_ini "Plantio" \
    --coluna_fim "Colheita" \
    --coluna_alvo "Tmax_media_veg"

# 3. ETo total entre datas customizadas (forçando soma)
python scripts/calcular_variavel_periodo.py \
    --planilha irrigacao.xlsx \
    --gpkg municipios.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel ETo \
    --coluna_ini "Inicio_irrig" \
    --coluna_fim "Fim_irrig" \
    --coluna_alvo "ETo_total_mm" \
    --agregacao soma

# 4. Umidade relativa média no florescimento (janela fixa)
python scripts/calcular_variavel_periodo.py \
    --planilha cafe.xlsx \
    --gpkg municipios.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --variavel RH \
    --coluna_ini "Inicio_flor" \
    --coluna_fim "Fim_flor" \
    --coluna_alvo "RH_media_flor" \
    --agregacao media
```

#### Pipeline completo (passo a passo)

```
Planilha + GeoPackage → Datas e códigos IBGE
       ↓
BR-DWGD (qualquer variável, 1 ou 3 arquivos)
       ↓
Detecta ordenação da latitude (v3.2.3 decrescente / v3.2.4 crescente)
       ↓
Subset espacial na bbox dos municípios + chunks para economia de RAM
       ↓
Pesos de área (pixel 0.1° × polígono municipal) — calculados uma única vez
       ↓
Para cada município: série temporal ponderada (extraída vetorialmente)
       ↓
Para cada registro (linha):
    Data inicial = coluna_ini, Data final = coluna_fim
    Soma ou média dos valores no intervalo [ini, fim]
       ↓
Escreve na coluna_alvo e salva planilha
```

#### Funcionamento detalhado

1. **Leitura flexível**: aceita sheets com uma ou múltiplas abas; se só houver uma, detecta automaticamente
2. **Auto-detecção de versão**: lê arquivos v3.2.3 (1 arquivo/var) ou v3.2.4 (3 arquivos/var) — funciona com ambos
3. **Ordenação da latitude**: detecta automaticamente se a latitude é crescente (v3.2.4) ou decrescente (v3.2.3)
4. **Subset inteligente**: expande a bbox dos municípios com `--buffer` (padrão 0.5°) e carrega apenas a região necessária
5. **Memória controlada**: usa `chunks={"time": 365}` e só carrega o subset espacial, evitando OOM
6. **Pesos de área reutilizáveis**: calcula uma vez, usa para todos os registros — essencial para performance
7. **Tratamento robusto de datas**: aceita múltiplos formatos e ignora registros com data inválida
8. **Estatísticas ao final**: exibe média, mediana, mínimo, máximo e desvio padrão dos resultados

#### Saída esperada (console)

```
===============================================================
📊 BR-DWGD — Cálculo Generalizado
===============================================================
  Variável:     pr → 'pr' no NetCDF
  Agregação:    SOMA
  Período:      'Antese' → '160dias_antese'
  Coluna alvo:  'Pr_160d_mm'
  Planilha:     PAM_CAFE_MATAS_clima.xlsx @ [DELTA PRODUTIVIDADE (brutos)]
===============================================================

[1/7] Lendo planilha...
  Colunas: ini=15, fim=20, cod=2, alvo=21
  Linhas: 2765 registros
  Registros com datas válidas: 2765/2765
[2/7] Carregando geometrias municipais...
  64 municípios, bbox: [-43.69, -40.77] × [-21.81, -18.84]
[3/7] Localizando arquivos NetCDF...
  Encontrados: 3 arquivo(s)
    pr_19610101_19801231_... (2.25 GB)
    pr_19810101_20001231_... (2.25 GB)
    pr_20010101_20251231_... (2.81 GB)
[4/7] Carregando dados...
    [1/3] pr_19610101_... OK (7305 dias, 30×29 px)
    [2/3] pr_19810101_... OK (7305 dias, 30×29 px)
    [3/3] pr_20010101_... OK (9131 dias, 30×29 px)
  Dados carregados: 23741 dias × 30 lat × 29 lon
  Período: 1961-01-01 a 2025-12-31
  Memória: 83 MB
[5/7] Calculando pesos de área...
  Pesos calculados para 64 municípios
[6/7] Extraindo séries municipais ponderadas...
  Municípios: 64/64 concluído
[7/7] Calculando SOMA no período 'Antese'→'160dias_antese'...
  Escrevendo 2765 resultados na coluna 'Pr_160d_mm'...
  ✅ 2765 valores escritos com sucesso!

📈 Estatísticas — Pr_160d_mm (pr)
  Registros:  2765
  Média:      990.10
  Mediana:    957.90
  Mín:        423.00
  Máx:        1843.20

✅ Processamento concluído!
```

#### Notas importantes

- O dado **ETo diário** no BR-DWGD v3.2.4 está em **mm/dia** (taxa). Para obter o total acumulado no período, use `--agregacao soma` — o script soma os valores diários.
- O dado **pr diário** está em **mm/dia** e `--agregacao soma` acumula corretamente.
- Para dados **mensais** (formato `--formato mensal`), a agregação `soma` para ETo funciona diretamente (já é total mensal).
- O script preserva **todas as outras colunas** da planilha — só altera a coluna alvo especificada.
- As fórmulas originais do Excel (ex: `=O2+160`) são mantidas intactas.

**Dependências:** `xarray netcdf4 geopandas openpyxl shapely numpy pandas`

---

## 5. ★ Geração de Mapas de Normais Climatológicas (Padrão PesquisAI)

Esta seção documenta o **fluxo definitivo para geração de mapas** de normais
climatológicas do BR-DWGD, estabelecido como padrão do PesquisAI após validação
com 66 mapas individuais e 6 mapas de comparação para a região das Matas de Minas.

### 5.1 Características do Padrão

| Característica | Especificação | Motivo |
|---|---|---|
| **Reamostragem** | Bilinear (`imshow`, `interpolation='bilinear'`) | Elimina o grid de pixels visível de `pcolormesh` |
| **Limites municipais** | Cinza, `linewidth=0.3`, alpha 0.4–0.6 | Contexto político-administrativo sem poluir |
| **Contorno da região** | Preto, `linewidth=1.8–2.0`, alpha 0.7–0.8 | Hierarquia visual clara (região > municípios) |
| **Idioma** | INGLÊS (títulos, legendas, colorbars) | Publicações internacionais, padronização |
| **BH** | `Pr − ETo × Kc` (Kc padrão = 1,05) | Balanço hídrico com coeficiente de cultivo |
| **Mapas individuais** | 11 períodos × 6 variáveis = 66 | Normais deslizantes 1975…2025 |
| **Mapas de comparação** | 3×3 grid, 9 diferenças consecutivas | Variação entre normais sucessivas (1985→2025) |
| **Fontes comparação** | Título geral 24pt, sub-títulos 20pt, colorbar 18pt | Legibilidade em publicações e apresentações |
| **DPI** | 200–250 (individual), 250 (comparação) | Qualidade para publicação |
| **Tamanho comparação** | figsize=(30, 28) com 250 DPI → ~6500×6200 px | Resolução suficiente para zoom e impressão |

### 5.2 Estrutura de saída

```
output_dir/
├── mapa_Tmean_1961-1974_MatasDeMinas.jpeg    (11 mapas)
├── mapa_Tmean_1961-1979_MatasDeMinas.jpeg
├── ...                                        (66 individuais)
├── mapa_BH_1995-2024_MatasDeMinas.jpeg
├── comparacao_Tmean_normais_consecutivas.jpeg (6 comparações)
├── comparacao_Tmax_normais_consecutivas.jpeg
├── comparacao_Tmin_normais_consecutivas.jpeg
├── comparacao_Pr_normais_consecutivas.jpeg
├── comparacao_ETo_normais_consecutivas.jpeg
└── comparacao_BH_normais_consecutivas.jpeg
```

### 5.3 Script principal

Use `scripts/gerar_mapa_normal_padrao.py` (incluso nesta skill):

```bash
python scripts/gerar_mapa_normal_padrao.py \
    --zip_pr "DATA_BR_DWGD/pr_Tmax_Tmin_NetCDF_Files.zip" \
    --zip_eto "DATA_BR_DWGD/ETo_u2_RH_Rs_NetCDF_Files.zip" \
    --gpkg "GIS/MUN_MATAS.gpkg" \
    --saida "NOVOS/" \
    --lat_min -21.5 --lat_max -19.0 \
    --lon_min -43.8 --lon_max -41.0 \
    --dpi 250 \
    --kc 1.05 \
    --idioma en
```

**Parâmetros:**

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--zip_pr` | (obrigatório) | Arquivo ZIP com NetCDFs de pr, Tmax, Tmin |
| `--zip_eto` | (obrigatório) | Arquivo ZIP com NetCDFs de ETo, u2, Rs, RH |
| `--gpkg` | (obrigatório) | GeoPackage com polígonos municipais |
| `--saida` | (obrigatório) | Diretório para salvar os JPEGs |
| `--lat_min` / `--lat_max` | (obrigatório) | Bounding box (latitude, WGS84) |
| `--lon_min` / `--lon_max` | (obrigatório) | Bounding box (longitude, WGS84) |
| `--dpi` | 200 | Resolução das figuras em DPI |
| `--kc` | 1.05 | Coeficiente de cultivo para BH |
| `--idioma` | `en` | `en` (inglês) ou `pt` (português) |
| `--extracao` | `/tmp/brdwgd_extract_std` | Diretório temporário |

### 5.4 Variáveis e períodos

**6 variáveis:**

| Variável | Label (EN) | Colormap | Agregação | Fonte |
|---|---|---|---|---|
| `Tmean` | Mean Temperature (°C) | Reds | Média | Derivada: (Tmax+Tmin)/2 |
| `Tmax` | Maximum Temperature (°C) | Reds | Média | BR-DWGD |
| `Tmin` | Minimum Temperature (°C) | Blues | Média | BR-DWGD |
| `Pr` | Precipitation (mm) | Blues | Soma | BR-DWGD |
| `ETo` | Reference Evapotranspiration (mm) | YlGn | Soma | BR-DWGD |
| `BH` | Water Balance (mm) | BrBG | Soma | Derivada: Pr − ETo × Kc |

**11 períodos deslizantes:**

| Ano Ref. | Período | Anos |
|---|---|---|
| 1975 | 1961–1974 | 14 |
| 1980 | 1961–1979 | 19 |
| 1985 | 1961–1984 | 24 |
| 1990 | 1961–1989 | 29 |
| 1995 | 1965–1994 | 30 |
| 2000 | 1970–1999 | 30 |
| 2005 | 1975–2004 | 30 |
| 2010 | 1980–2009 | 30 |
| 2015 | 1985–2014 | 30 |
| 2020 | 1990–2019 | 30 |
| 2025 | 1995–2024 | 30 |

### 5.5 Algoritmo de plotagem (individual)

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 10))

# ── Bilinear (elimina pixel grid) ──
extent = [lon0 - 0.05, lonN + 0.05, lat0 - 0.05, latM + 0.05]
im = ax.imshow(valores_2d, extent=extent, origin='lower',
               cmap=cfg['cmap'], interpolation='bilinear', aspect='auto')

# ── Hierarquia de limites ──
gdf_municipios.boundary.plot(ax=ax, color='gray', linewidth=0.3, alpha=0.6)
gdf_regiao.boundary.plot(ax=ax, color='black', linewidth=2.0, alpha=0.8)

# ── Colorbar ──
plt.colorbar(im, ax=ax, shrink=0.7).set_label(cfg['label'], fontsize=11)

# ── Título em inglês ──
ax.set_title(f"Climatological Normal {ano_ref}\n{var_en} — Matas de Minas",
             fontsize=13, fontweight='bold')
ax.set_xlabel('Longitude (°)', fontsize=11)
ax.set_ylabel('Latitude (°)', fontsize=11)

plt.savefig(saida_path, dpi=200, bbox_inches='tight')
plt.close()
```

### 5.6 Algoritmo de plotagem (comparação 3×3)

```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(30, 28))
gs = GridSpec(3, 3, figure=fig, hspace=0.30, wspace=0.20)

for idx, (diff, (la, lb)) in enumerate(zip(diffs, valid_labels)):
    ax = fig.add_subplot(gs[idx // 3, idx % 3])
    ax.imshow(diff, extent=extent, origin='lower',
              cmap='RdBu_r', interpolation='bilinear',
              aspect='auto', vmin=-vmax, vmax=vmax)
    ax.set_title(f"Normal {la} vs. {lb}", fontsize=20, fontweight='bold')
    ax.tick_params(labelsize=14)

cbar_ax = fig.add_axes([0.92, 0.12, 0.018, 0.76])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label("difference (mm)", fontsize=18)
cbar.ax.tick_params(labelsize=16)

fig.suptitle(f"Variation Between Consecutive Normals — {var} — Matas de Minas",
             fontsize=24, fontweight='bold')
plt.savefig(fpath, dpi=250, bbox_inches='tight')
```

### 5.7 BH — Balanço Hídrico com coeficiente de cultivo (Kc)

O balanço hídrico é calculado como:

$$ BH = Pr - (ETo \times Kc) $$

Onde:
- `Pr` = Precipitação anual total (mm)
- `ETo` = Evapotranspiração de referência anual total (mm)
- `Kc` = Coeficiente de cultivo (padrão: 1,05 para cafeeiro em produção)

**Interpretação dos valores de BH:**

| BH | Significado |
|---|---|
| BH > 0 | Excedente hídrico — precipitação supera a demanda evaporativa |
| BH ≈ 0 | Equilíbrio hídrico |
| BH < 0 | Déficit hídrico — demanda evaporativa supera a precipitação |

### 5.8 Colormaps recomendados

| Tipo de variável | Colormap | Alternativa |
|---|---|---|
| Temperatura (média/máx) | `Reds` | `YlOrRd` |
| Temperatura (mínima) | `Blues` | `YlGnBu` |
| Precipitação | `Blues` | `YlGn` |
| Evapotranspiração | `YlGn` | `Greens` |
| Balanço hídrico | `BrBG` | `RdBu` (centrado em zero) |
| Diferenças (comparação) | `RdBu_r` | `RdBu` (centrado em zero) |

### 5.9 Notas importantes

1. **A latitude cresce de sul para norte na v3.2.4.** Use `slice(lat_min, lat_max)`.
   Verifique com `print(ds.latitude.values[:3], ds.latitude.values[-3:])`.

2. **Os arquivos diários são volumosos.** Faça o subset espacial ANTES de carregar
   com `.load()`. O subset da região de café (~25×28 pixels) cabe em ~114 MB
   para ~23.700 dias.

3. **ETo diário está em mm/dia** (taxa). Para obter o total anual, some os valores
   diários. O script `gerar_mapa_normal_padrao.py` faz isso automaticamente.

4. **Periodicidade:** Os 4 períodos iniciais (1975–1990) têm menos de 30 anos
   porque não há dados anteriores a 1961. A partir de 1995, todos têm 30 anos
   completos.

5. **Citação obrigatória em cada figura:** Incluir referência a Xavier et al. (2022)
   na legenda ou rodapé do artigo/publicação que usar as figuras.

---

## 6. Problemas comuns e soluções

| Problema | Causa | Solução |
|---|---|---|
| `KeyError: 'latitude'` | Dimensão nomeada `lat` | `ds = ds.rename({"lat": "latitude", "lon": "longitude"})` |
| Resolução ≠ 0.1° | Reamostragem acidental | Não usar `.interp()` ou `.coarsen()` |
| Memória insuficiente (dados diários) | Arquivo sem chunks | `xr.open_dataset(..., chunks={"time": 365})` + subset antes de `.load()` |
| Arquivo não encontrado | Nomenclatura diferente | Listar arquivos com `os.listdir()` e verificar padrão |
| `gdown` falha em pasta grande | Sem `--remaining-ok` | Usar `gdown.download_folder(..., remaining_ok=True)` |
| ETo com valores estranhos | Confundiu mm/mês com mm/dia | Mensal = já é total; diário = taxa × dias |
| Tmean não encontrada | Só existe nos mensais | Calcular: `(Tmax + Tmin) / 2` |
| Latitude ordenação errada | v3.2.3 vs v3.2.4 | v3.2.3: decrescente; **v3.2.4: crescente**. Verificar com `print(ds.latitude.values[:3])` |
| Subset vazio (0 lat) | slice na ordem errada | Latitude crescente: `slice(lat_min, lat_max)` |
| NaN em municípios | Município fora da bbox | Verificar intersecção com `gdf.cx` |
| `CD_MUN` não casa | Int vs string no GeoPackage | `gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)` |
| Planilha não salva | Workbook aberto em outro programa | Fechar Excel antes de executar |
| Coluna não encontrada | Acento ou espaço no nome | Verificar header exato da planilha |
| GD negativo acumulando | Temperatura base maior que Tmed | GD < 0 são zerados (não acumulam) |
| Soma térmica nunca atinge alvo | Ano muito frio ou partida tardia | Verificar `data_inicio` e `soma_alvo` |
| Antese_v2 anterior à data de partida | Data de partida errada | `Dec_abril_16mm` deve vir antes da antese |
| Tmax/Tmin não encontrados | Nomenclatura diária v3.2.4 vs v3.2.3 | Tmax (maiúsculo) na v3.2.4, tmax (minúsculo) na v3.2.3 |
| ETo_antese_mm não calcula | Coluna de data vazia | Verificar se `Antese` está preenchida como data válida (YYYY-MM-DD) |
| Janela de 15 dias sai do período | Data próxima a 1961 ou 2025 | O código ajusta automaticamente os limites: `max(0, idx-N)` e `min(total, idx+M)` |
| Quota excedida ao baixar pr | Muitos downloads do zip 7,7 GB | **Perguntar ao pesquisador** se deseja aguardar ~24h, usar aproximação alternativa, ou tentar outra fonte |
| Vírus scan no download do ETo | Arquivo > 100 MB | Usar `requests` com UUID/confirm (seção 2.1) |
| Soma dos pesos ≠ 1 | Erro de arredondamento | Valores entre 0,999 e 1,001 são aceitáveis para float32 |
| `--sheet` não encontrada | Nome com acento ou espaço | Usar `--sheet "Nome Exato"` (com aspas) |
| Variável não reconhecida | Capitalização errada | `calcular_variavel_periodo.py` aceita: pr, PR, Pr, ETo, eto, ETO, Tmax, tmax, etc. |
| Data fora do período 1961-2025 | Dado não cobre a data | Verificar se a data está entre 1961-01-01 e 2025-12-31 |
| Todas as datas como "fora do período" | Formato de data não reconhecido | Usar YYYY-MM-DD ou DD/MM/YYYY na planilha |
| ETo acumulado parece alto | ETo diário é mm/dia (taxa), não total | O script soma automaticamente; o resultado é o total do período em mm |
| Nenhum arquivo encontrado para variável | Arquivos NetCDF em outro diretório | Usar `--dir_dados` apontando para a pasta com os arquivos .nc |
| Muitos municípios sem geometria | Código IBGE não bate com GPKG | `gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)` — códigos IBGE devem ser string |

---

## 6. Citação obrigatória

> Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022).
> New improved Brazilian daily weather gridded data (1961–2020).
> *International Journal of Climatology*, 42(16), 8390–8404.
> https://doi.org/10.1002/joc.7731

---

## 7. Referências adicionais

- `references/variaveis_e_periodos.md` — detalhes de variáveis, períodos OMM e convenções
- `scripts/calcular_normal.py` — script completo para normais (dados diários)
- `scripts/extrair_municipios.py` — extração municipal com ponderação por área
- `scripts/processar_dec_abril_16mm.py` — cálculo de limiar de precipitação acumulada
- `scripts/calcular_antese_v2.py` — cálculo de soma térmica (graus-dia)
- `scripts/calcular_janela_acumulo.py` — cálculo de variáveis em janela centrada
- **`scripts/calcular_variavel_periodo.py`** 🚀 — **★ GENERALIZADO: calcula qualquer variável BR-DWGD para qualquer período. O script mais versátil da skill.**
- `scripts/plotar_normal.py` — visualização de normais (básico)
- **`scripts/gerar_mapa_normal_padrao.py`** ⭐ — **★ GERAÇÃO DEFINITIVA de mapas (padrão PesquisAI): bilinear, inglês, hierarquia de limites, BH = Pr − ETo × Kc, comparação 3×3 com fontes grandes**
