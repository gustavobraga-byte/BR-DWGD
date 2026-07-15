# br-dwgd-normals

**BR-DWGD — Normais Climatológicas & Séries Municipais**

Skill para baixar, processar e calcular **normais climatológicas** a partir dos dados do
**Brazilian Daily Weather Gridded Data (BR-DWGD)**, bem como extrair **séries temporais
municipais** com ponderação por área de interseção pixel × município.

> **Resolução espacial obrigatória: 0.1° × 0.1°** — nunca faça reamostragem ou altere essa resolução ao longo do fluxo de trabalho.

> ⚠️ **Âmbito de aplicação — a skill NÃO é exclusiva para as Matas de Minas.**
> Os exemplos e os nomes de arquivos de demonstração (`MUN_MATAS.gpkg`,
> `PAM_CAFE_MATAS_clima.xlsx`) referem-se apenas a um **caso de uso ilustrativo**
> (cafeicultura das Matas de Minas). A grade BR-DWGD cobre **todo o território
> brasileiro** (latitudes ≈ −34° a +5°, longitude ≈ −74° a −34°) na resolução 0,1°.
> Basta fornecer o GeoPackage dos municípios de interesse e a planilha correspondente
> para aplicar a skill a **qualquer estado, bacia, região ou município do Brasil**.

---

## Contribuição

Esta skill é uma **contribuição de Antônio Consentino Teixeira Oliveira**,
**agrônomo** e **mestrando em Extensão Rural pela Universidade Federal de Viçosa (UFV)**.

O desenvolvimento foi inicialmente voltado a aplicações agrometeorológicas — em especial
à cafeicultura das Matas de Minas — cobrindo desde o cálculo de normais climatológicas
até a determinação de datas fenológicas (antese) por soma térmica e a geração de mapas
padronizados para publicação. Contudo, por construção, a skill é **genérica e aplicável
a qualquer recorte espacial do Brasil** (ver nota de âmbito acima).

---

## Citação científica recomendada

Ao utilizar esta skill e os dados BR-DWGD em trabalhos acadêmicos, cite a fonte original
do conjunto de dados:

> **XAVIER, A. C.; KING, C. W.; SCANLON, B. R.** Daily gridded meteorological variables
> in Brazil (1980–2013). *Scientific Data*, v. 3, p. 160036, 2016.

> 💡 A versão de dados empregada nesta skill é a **v3.2.4** (atualizada e estendida até
> 2025), derivada do mesmo produto de Xavier et al. (2016). Recomenda-se citar o artigo
> original acima e, quando aplicável, mencionar a versão específica do BR-DWGD utilizada.

---

## O que esta skill faz

- **Baixa dados BR-DWGD** (v3.2.3 e v3.2.4), diários ou mensais, do Google Drive,
  contornando o aviso de *virus scan* em arquivos grandes (> 100 MB).
- **Calcula normais climatológicas** de 30 anos (OMM: 1961–1990, 1971–2000,
  1981–2010, 1991–2020) ou períodos customizados, para 8 variáveis.
- **Extrai séries municipais ponderadas por área** (interseção pixel 0,1° × polígono
  municipal), reutilizando os pesos de uma única vez.
- **Determina datas de atingimento de limiares**, como:
  - Primeiro dia a partir de 1º de abril com precipitação acumulada ≥ 16 mm
    (`Dec_abril_16mm`);
  - Data de florescimento (antese) por soma térmica de graus-dia (`Antese_v2`,
    soma-alvo 1980 °C-dia, temperatura base 8,5 °C para café arábica).
- **Calcula janelas acumuladas centradas em data de referência** (ex.: ETo ou Pr em
  15 dias ao redor da antese).
- **Gera mapas padronizados** de normais (interpolação bilinear, limites municipais,
  rótulos em inglês, balanço hídrico `BH = Pr − ETo × Kc`).

### Variáveis suportadas

| Variável | Nome NetCDF | Unidade | Agregação (normal) |
|---|---|---|---|
| Precipitação | `pr` | mm | Soma |
| Temperatura máxima | `Tmax` | °C | Média |
| Temperatura mínima | `Tmin` | °C | Média |
| Temperatura média | `Tmean` | °C | Média |
| Radiação solar | `Rs` | MJ/m² | Média |
| Umidade relativa | `RH` | % | Média |
| Vento (2 m) | `u2` | m/s | Média |
| Evapotranspiração de referência | `ETo` | mm | Soma |

---

## Estrutura da pasta

```
br-dwgd-normals/
├── SKILL.md                  # Documentação completa e fluxos de trabalho
├── README.md                 # Este arquivo
├── references/
│   └── variaveis_e_periodos.md
└── scripts/
    ├── calcular_normal.py              # Normais de 30 anos (CLI) — diário
    ├── extrair_municipios.py           # Séries municipais ponderadas — mensal
    ├── processar_dec_abril_16mm.py     # 1º dia com Pr acumulada ≥ limiar
    ├── calcular_antese_v2.py           # Data de atingimento de soma térmica ⭐
    ├── calcular_janela_acumulo.py      # Soma em janela centrada na referência 🆕
    ├── calcular_variavel_periodo.py    # ★ GENERALIZADO: qualquer var./período 🚀
    ├── plotar_normal.py                # Mapas básicos (pcolormesh, PT)
    └── gerar_mapa_normal_padrao.py     # ★ GERAÇÃO DEFINITIVA de mapas ⭐
```

---

## Início rápido

### 1. Cálculo generalizado (recomendado)

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

### 2. Data de antese por soma térmica

```bash
python scripts/calcular_antese_v2.py \
    --planilha PAM_CAFE_MATAS_clima.xlsx \
    --gpkg MUN_MATAS.gpkg \
    --dir_dados /tmp/br-dwgd-daily \
    --coluna_dec "Dec_abril_16mm" \
    --coluna_antese_v2 "Antese_v2" \
    --soma_alvo 1980.0 \
    --base_temp 8.5
```

### 3. Geração de mapas padronizados

```bash
python scripts/gerar_mapa_normal_padrao.py \
    --zip_pr "DATA_BR_DWGD/pr_Tmax_Tmin_NetCDF_Files.zip" \
    --zip_eto "DATA_BR_DWGD/ETo_u2_RH_Rs_NetCDF_Files.zip" \
    --gpkg "GIS/MUN_MATAS.gpkg" \
    --saida "NOVOS/" \
    --dpi 250 --kc 1.05 --idioma en
```

Consulte o `SKILL.md` para a documentação detalhada de cada fluxo, parâmetros e
exemplos de saída.

---

## Dependências

`xarray`, `netcdf4`, `geopandas`, `openpyxl`, `shapely`, `numpy`, `pandas`, `gdown`,
`matplotlib`.

```bash
pip install xarray netcdf4 geopandas openpyxl shapely numpy pandas gdown matplotlib
```

---

## Fonte de dados

- **BR-DWGD (Xavier et al., 2016)** 
- Xavier, A. C., C. W. King, and B. R. Scanlon. 2016. “Daily Gridded Meteorological Variables in Brazil (1980–2013).” International Journal of Climatology 36, no. 6: 2644–2659. https://doi.org/10.1002/joc.4518. 
- Downloads mensais (~5 MB/var) e diários (v3.2.4) via Google Drive (ver `SKILL.md`, seção 2).

---

## Licença e uso

Skill disponibilizada para fins de pesquisa e extensão rural. Ao utilizar os resultados
em publicações, **cite obrigatoriamente a fonte original dos dados** (Xavier et al., 2016,
conforme a seção *Citação científica recomendada*).

**Autoria da skill:** Antônio Consentino Teixeira Oliveira — Agrônomo, Mestrando em
Extensão Rural (UFV).
