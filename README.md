# 🌍 Global Migration Observatory

> **Tagline**: Explore where people migrate, how migration patterns change, and how migration relates to socioeconomic factors.

---

## 📌 Overview

The **Global Migration Observatory** is an empirical data platform designed to analyze global migration dynamics, spatial patterns, and macroeconomic correlations across countries and corridors over three decades (1990–2020).

This repository contains:
- **Phase 1: Foundation + Data Ingestion + Cleaning + Validation**: Complete backend data pipeline, ISO-3 standardization engine, automated 14-rule validation suite, and reproducible processed datasets.
- **Phase 2: Interactive Migration Explorer**: Professional multi-page Streamlit exploration dashboard featuring choropleths, time-series trends, country rankings, bilateral corridor analytics, country profiles, and contextual CSV data downloads.
- **Phase 3: Migration Network & Advanced Corridor Analysis**: Graph-theoretic network modeling using NetworkX, interactive 2D force-directed and circular network graphs, geographic corridor maps, network centrality metrics (Degree, Weighted Strength, Betweenness, PageRank), Louvain/modularity community detection, bidirectional corridor asymmetry analysis, and universal **Light Mode (☀️) / Dark Mode (🌙)** theming.

---

## 🧭 Dashboard Architecture & Pages (Phase 3)

The application provides eleven analytical views accessible via the sidebar:

1. **🏠 Overview**:
   - Dynamic KPI cards (*Total Migrant Stock*, *Countries Tracked*, *Top Destination by Stock*, *Top Destination by Share of Population*, *Active Corridors*) for any chosen census year.
   - Global stock trajectory (1990–2020) and Top 10 destination horizontal bar chart.
   - Summary data table with direct CSV download.
2. **🌍 Global Map**:
   - Interactive Plotly choropleth world map with metric selection (*Migrant Stock*, *Migrant Stock % of Population*, *5-Year Stock Change*, *5-Year Stock Growth %*).
   - Quinquennial census round selector (1990–2020).
   - Rich hover tooltips with sovereign rank, share, population, and stock.
   - Filterable country table with CSV download.
3. **📈 Trends**:
   - Long-term global aggregate migrant stock trajectory across 1990–2020.
   - Multi-country comparative time series with country multi-selector and metric switcher.
   - Comparative data table with CSV download.
4. **🏆 Rankings**:
   - Dynamic Top 10, Top 25, or Top 50 country rankings by chosen metric.
   - Interactive horizontal bar charts and sort order toggles (*Highest First* / *Lowest First*).
   - Comprehensive ranking table with CSV download.
5. **🔀 Route Explorer**:
   - Global Top Bilateral Corridors (Top 10, 25, 50) horizontal bar chart (`Origin → Destination | Migrant Stock`).
   - Interactive corridor filter: Origin $\to$ Destination, Origin only, or Destination only.
   - Corridor share metrics (% of origin emigrant stock, % of destination immigrant stock).
   - Corridor data table with CSV download.
6. **🌎 Country Explorer**:
   - Deep dive country profile with top metric banner (*Stock*, *Population*, *Share %*, *Global Rank*, *GDP/Capita*).
   - 5 analytical sub-modules:
     - *Stock Trajectory (1990–2020)*
     - *Inbound & Outbound Bilateral Corridors*
     - *🕸️ Network Centrality Profile & Ego Network*
     - *Global Rank History*
     - *Macroeconomic Context (GDP, GDP/Capita, Population, Unemployment)*
   - Full historical time-series data table with CSV download.
7. **🕸️ Migration Network**:
   - Interactive 2D Network visualization (Spring, Circular, Kamada-Kawai layouts) with node scaling by centrality and edge thickness by migrant stock.
   - Geographic Network map with geodesic bilateral arcs between country centroids.
   - Centrality rankings bar charts and tables.
   - Longitudinal network evolution metrics (1990–2020).
   - Multi-country longitudinal centrality trajectory comparison.
8. **🔗 Corridor Analysis**:
   - Bidirectional country pair analysis with directional asymmetry indices and dominant flow determination.
   - Herfindahl-Hirschman Index (HHI) destination concentration analysis for emigrant stocks.
   - Global top 50 corridors master table.
9. **🌐 Communities**:
   - Louvain and modularity community detection discovering dense migrant-stock clusters.
   - Interactive community cluster network graph.
   - Cluster summary and member drill-down inspector with CSV export.
10. **ℹ️ Methodology**:
    - Documentation of UN DESA 2020 Revision and World Bank WDI datasets.
    - Mathematical definitions of all network metrics and derived formulas.
    - Scientific emphasis on **Migrant Stock $\neq$ Annual Migration Flow**.
11. **⚙️ Settings**:
    - Universal Theme switcher: **☀️ Light Mode** and **🌙 Dark Mode**.
    - Streamlit cache manager.

---

## ⚠️ Critical Methodological Principle: Migrant Stock vs. Migration Flow

A core architectural principle of the Global Migration Observatory is the strict separation between **Migrant Stock** and **Migration Flow**:

| Dimension | International Migrant Stock (This Dataset) | Migration Flow |
| :--- | :--- | :--- |
| **Definition** | Estimated number of foreign-born individuals residing in a destination country at a mid-year point in time. | Number of individuals moving across borders over a specific period (e.g. annual entries/exits). |
| **Measurement Unit** | People residing at time $t$ | Moves / events per year |
| **Components of Change** | Includes net immigration, deaths of migrants, return migration, naturalization, and census reclassifications. | Border crossing counts only. |
| **UN Revision** | Official 5-year census rounds (1990, 1995, 2000, 2005, 2010, 2015, 2020). | Administrative entry registers (UNHCR, OECD, national border registries). |

> [!IMPORTANT]
> **Intercensal stock changes are NOT annual migration flows.** Intercensal differences between 5-year rounds reflect net cumulative changes in the residing foreign-born population, not gross annual border crossings.

---

## 🗂️ Project Structure

```
global-migration-observatory/
│
├── app.py                      # Multi-page interactive Streamlit dashboard (Phases 1, 2, 3)
├── run_pipeline.py             # Root runner script for end-to-end data pipeline
├── config.yaml                 # Central configuration for paths, indicators, and URLs
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Complete documentation
├── .gitignore                  # Git ignore rules
│
├── data/
│   ├── raw/
│   │   ├── migration/          # Official UN DESA Excel workbooks
│   │   └── world_bank/         # Cached World Bank API JSON responses
│   │
│   ├── processed/              # Reproducible cleaned and merged datasets
│   │   ├── migration_destination_cleaned.csv
│   │   ├── migration_bilateral_cleaned.parquet
│   │   ├── world_bank_cleaned.csv
│   │   ├── migration_country_socioeconomic.csv
│   │   └── country_reference.csv
│   │
│   └── reports/                # Automated data quality & validation reports
│       ├── data_quality_report.csv
│       └── data_quality_summary.md
│
├── src/
│   ├── __init__.py             # Package initializer
│   ├── config.py               # Typed configuration loader & path resolver
│   ├── utils.py                # ISO-3 resolver, entity classifier & M49 database
│   ├── ui_theme.py             # Universal Light Mode & Dark Mode styling engine
│   ├── data_loader.py          # UN DESA downloader & World Bank API client
│   ├── data_cleaning.py        # Wide-to-long reshaping & standardization
│   ├── data_validation.py      # 14-rule data validation engine & report generator
│   ├── data_merging.py         # Country-year and corridor-level merge logic
│   ├── feature_engineering.py  # Derived metrics (shares, growth, rankings)
│   ├── dashboard_data.py       # Analytical queries & cached data layer for dashboard
│   ├── network_analysis.py     # NetworkX graph construction, centralities, communities
│   ├── network_visualization.py# 2D spring/circular, geographic arc, and cluster plots
│   └── pipeline.py             # End-to-end pipeline runner
│
├── notebooks/
│   └── 01_data_exploration.ipynb  # Interactive EDA and visualization notebook
│
└── tests/
    ├── test_data_loader.py
    ├── test_data_cleaning.py
    ├── test_data_validation.py
    ├── test_feature_engineering.py
    ├── test_dashboard_data.py
    ├── test_streamlit_pages.py
    └── test_network_analysis.py
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```powershell
git clone https://github.com/shrutisrivastava-star/world_migration.git
cd world_migration
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 Execution & Usage

### 1. Run Full End-to-End Data Pipeline
```powershell
python run_pipeline.py
```

### 2. Run Test Suite (42 Tests)
```powershell
pytest -v
```

### 3. Launch Interactive Streamlit Dashboard
```powershell
streamlit run app.py
```

---

## 🔬 Network Metric & Feature Formulations

1. **In-Degree & Out-Degree**:
   $$\text{In-Degree}(v) = |\{u \mid (u, v) \in E\}|, \quad \text{Out-Degree}(u) = |\{v \mid (u, v) \in E\}|$$

2. **Weighted Strength**:
   $$\text{In-Strength}(v) = \sum_{u} W(u, v), \quad \text{Out-Strength}(u) = \sum_{v} W(u, v)$$

3. **Betweenness Centrality**:
   $$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

4. **Bidirectional Asymmetry Index**:
   $$\text{Asymmetry Index}_{A \leftrightarrow B} = \frac{S_{A \to B} - S_{B \to A}}{S_{A \to B} + S_{B \to A}} \in [-1.0, 1.0]$$

5. **Community Modularity**:
   $$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

---

## 🔍 Validation & Test Status

- **Automated Validation Checks**: 14 / 14 Passed (100%)
- **Pytest Suite**: 42 / 42 Unit & Integration Tests Passed (100%)
- **Streamlit Health Check**: HTTP 200 OK across all pages
- **Themes**: Verified in both ☀️ Light Mode and 🌙 Dark Mode
