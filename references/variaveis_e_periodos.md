# BR-DWGD — Variáveis, Períodos, Convenções e Dicas

## Variáveis disponíveis

| Variável | Nome NetCDF | Unidade | Tipo agregação | Arquivo mensal v3.2.4 |
|---|---|---|---|---|
| Precipitação | `pr` | mm | **Soma** | `pr_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| Temperatura máxima | `Tmax` | °C | Média | `Tmax_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| Temperatura mínima | `Tmin` | °C | Média | `Tmin_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| Temperatura média | `Tmean` | °C | Média | `Tmean_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| Radiação solar | `Rs` | MJ/m² | Média | `Rs_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| Umidade relativa | `RH` | % | Média | `RH_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| Veloc. vento 2m | `u2` | m/s | Média | `u2_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |
| ETo ref. | `ETo` | mm | **Soma (já total)** | `ETo_1961_2025_BR-DWGD_monthly_v_3.2.4.nc` |

> ⚠️ **Capitalização importa!** Nos arquivos mensais: `Tmax`, `Tmin`, `Tmean` (T maiúsculo),
> `pr`, `ETo`, `Rs`, `RH`, `u2` (primeira letra minúscula).
> Nos arquivos **diários** v3.2.3: todos minúsculos (`tmax`, `tmin`, `pr`, etc.).
> Nos arquivos **diários** v3.2.4: minúsculos (`pr`).

## Cobertura temporal por versão

| Versão | Início | Fim | Formato | Variáveis |
|---|---|---|---|---|
| v3.2.3 (estável) | 1961-01-01 | 2024-03-20 | Diário | Todas (pr, Tmax, Tmin, Rs, RH, u2, ETo) |
| v3.2.4 mensal | 1961-01 | 2025-12 | **Mensal** | Todas + Tmean |
| **v3.2.4 diário** ⭐ | **1961-01-01** | **2025-12-31** | **Diário (3 arquivos)** | **pr, Tmax, Tmin** |

### Arquivos diários v3.2.4 (detalhes)

A versão v3.2.4 diária divide cada variável em 3 arquivos de ~2.2–2.8 GB:

| Variável | 1961–1980 | 1981–2000 | 2001–2025 |
|---|---|---|---|
| **pr** | `pr_19610101_19801231_..._v_3.2.4.nc` | `pr_19810101_20001231_..._v_3.2.4.nc` | `pr_20010101_20251231_..._v_3.2.4.nc` |
| **Tmax** | `Tmax_19610101_19801231_..._v_3.2.4.nc` | `Tmax_19810101_20001231_..._v_3.2.4.nc` | `Tmax_20010101_20251231_..._v_3.2.4.nc` |
| **Tmin** | `Tmin_19610101_19801231_..._v_3.2.4.nc` | `Tmin_19810101_20001231_..._v_3.2.4.nc` | `Tmin_20010101_20251231_..._v_3.2.4.nc` |

> Os 3 arquivos são concatenáveis ao longo da dimensão `time`.

## ⚠️ Ordenação da latitude: v3.2.3 vs v3.2.4

**Esta é a diferença mais crítica entre as versões!**

| Versão | Ordem latitude | Primeiros valores | slice correto |
|---|---|---|---|
| **v3.2.3** (diário estável) | **Decrescente** (5°N → -34°S) | `5.35, 5.25, ..., -33.85` | `slice(lat_max, lat_min)` |
| **v3.2.4** (diário novo) | **Crescente** (-34°S → 5°N) | `-33.85, -33.75, ..., 5.35` | `slice(lat_min, lat_max)` |
| **v3.2.4** mensal | **Crescente** (-34°S → 5°N) | `-33.85, ..., 5.35` | `slice(lat_min, lat_max)` |

**Sempre verifique antes de recortar:**
```python
print("Primeiros 3 valores de latitude:", ds.latitude.values[:3])
print("Últimos 3 valores de latitude:", ds.latitude.values[-3:])
```

## Períodos de normal climatológica

### Períodos OMM (30 anos)

| Período | Status | Disponível? |
|---|---|---|
| 1961–1990 | Histórico | ✅ (ambas versões) |
| 1971–2000 | Histórico | ✅ |
| 1981–2010 | Anterior | ✅ |
| 1991–2020 | **Vigente (atual)** | ✅ |

### Períodos não-OMM (decadais e customizados)

Para análise de mudanças recentes, use também:

| Período | Descrição |
|---|---|
| 2001–2010 | 1ª década séc. XXI |
| 2011–2020 | 2ª década séc. XXI |
| 2021–2025 | 1º quinquênio atual |
| 1971–2000 → 1981–2010 | Diferença entre normais de 30 anos |
| 1991–2020 → 1981–2010 | Diferença entre normais de 30 anos |

## Grade espacial

| Atributo | Valor |
|---|---|
| Resolução | **0.1° × 0.1°** (~11 km) |
| Cobertura | Brasil continental |
| Sistema ref. | WGS84 / EPSG:4326 (compatível com EPSG:4674) |
| Dimensões (Brasil) | 393 lat × 391 lon pixels |
| Dimensões (ex: Matas de Minas) | ~25 lat × ~24 lon = ~600 pixels |

## ETo: taxas vs totais

| Formato | Valor no NetCDF | Para obter anual |
|---|---|---|
| **Mensal** v3.2.4 | Total do mês (mm/mês) | Somar 12 meses |
| **Diário** v3.2.3 | Taxa (mm/dia) | Somar: `sum(rate * days_in_month)` |

```python
# Mensal (fácil)
eto_anual = ds.ETo.values.sum(axis=0)

# Diário (cuidado)
dim = np.array([calendar.monthrange(y, m)[1] for y, m in zip(years, months)])
eto_anual = (ds.ETo.values * dim[:, None, None]).sum(axis=0)
```

## Janela de 15-set a 15-nov para cafeicultura

Dados mensais (aproximação boa):
```python
# Pesos: set=0.25, out=0.50, nov=0.25 (proporção de dias na janela)
rh_window = 0.25 * rh_set + 0.50 * rh_out + 0.25 * rh_nov
```

Dados diários (preciso):
```python
# Dia 258 = 15 set, dia 319 = 15 nov (não bissexto)
rh_window = ds_rh.sel(time=ds_rh.time.dt.dayofyear.isin(range(258, 320)))
rh_mean = rh_window.mean(dim="time")
```

## Tamanho e memória

| Tipo | Tamanho/arquivo | RAM necessária |
|---|---|---|
| Mensal v3.2.4 | ~5 MB | 50 MB (cabe inteiro) |
| Diário v3.2.3 (1 var) | ~1.2 GB | ~6 GB sem chunks |
| Diário v3.2.4 (1 var, 3 arquivos) | ~2.2–2.8 GB / arquivo | Precisa de chunks + subset |
| Diário v3.2.4 RH | ~2.2 GB (zip) / ~5 GB (nc) | Precisa de chunks |
| Subset Matas de Minas (diário) | ~114 MB (para todos os dias) | Cabe em RAM após subset |

Sempre usar chunks para dados diários e fazer subset espacial antes de `.load()`:
```python
ds = xr.open_dataset("arquivo.nc", chunks={"time": 365})
# Subset espacial ANTES de carregar
ds_sub = ds.sel(latitude=slice(lat_min, lat_max), longitude=slice(lon_min, lon_max))
ds_sub = ds_sub.load()
```

## Problemas comuns

| Problema | Causa | Solução |
|---|---|---|
| `KeyError: 'latitude'` | Dimensão `lat`/`lon` | `ds.rename({"lat":"latitude","lon":"longitude"})` |
| Resolução ≠ 0.1° | Reamostragem | Não usar `.interp()` ou `.coarsen()` |
| OOM com diários | Sem chunks | `chunks={"time": 365}` + subset antes de `.load()` |
| `gdown` falha | Link de pasta vs arquivo | Usar `gdown.download_folder()` para pastas; `gdown.download()` para arquivos individuais |
| ETo muito alto/baixo | Confundiu total vs taxa | Ver seção ETo acima |
| Tmean não encontrada | Só existe nos mensais | Calcular como `(Tmax+Tmin)/2` |
| NaN em municípios | Município fora da bbox | Verificar intersecção com `gdf.cx` |
| Subset vazio (0 lat na v3.2.4) | slice na ordem errada | Latitude CRESCENTE → `slice(lat_min, lat_max)` |
| CD_MUN não corresponde | int vs string | `gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)` |
| Arquivo não baixou | Drive cota excedida | Esperar ou usar `--resume` do gdown |
