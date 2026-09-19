# 🌍 Global Migration Observatory

> **Tagline**: Explore where people migrate, how migration patterns change, and how migration relates to socioeconomic factors.

---

## 📌 Overview

The **Global Migration Observatory** is an academic-grade empirical data platform designed to analyze global migration dynamics, spatial network topologies, concentration patterns, macroeconomic correlations, and automated data storytelling across countries and corridors over three decades (1990–2020).

This repository contains:
- **Phase 1: Foundation + Data Ingestion + Cleaning + Validation**: Complete backend data pipeline, ISO-3 standardization engine, automated 14-rule validation suite, and reproducible processed datasets.
- **Phase 2: Interactive Migration Explorer**: Multi-page Streamlit exploration dashboard featuring choropleths, time-series trends, country rankings, bilateral corridor analytics, country profiles, and contextual CSV data downloads.
- **Phase 3: Migration Network & Advanced Corridor Analysis**: Graph-theoretic network modeling using NetworkX, interactive 2D force-directed and circular network graphs, geographic corridor maps, network centrality metrics (Degree, Weighted Strength, Betweenness, PageRank), modularity community detection, bidirectional corridor asymmetry analysis, and universal **Light Mode (☀️) / Dark Mode (🌙)** theming.
- **Phase 5: Advanced Migration Analytics & Data Storytelling**: Concentration indices (Herfindahl-Hirschman Index - HHI), 5-year intercensal growth classifications, socioeconomic bivariate correlations (Pearson & Spearman), transparent outlier detection (IQR & Z-score), multi-country comparative profiling with normalized relative scores, and deterministic rule-based automated data storytelling.

---

## 🧭 Dashboard Architecture & Pages

The application provides fourteen analytical views accessible via the categorized sidebar:

### 🌐 CORE EXPLORER
1. **🏠 Overview**: Executive summary with global KPI cards (*Total Migrant Stock*, *Global Migrant Share*, *Reporting Nations*, *Top Destination*, *Active Corridors*), 1990–2020 global stock trajectory, and top 10 destination rankings.
2. **🌍 Global Map**: Interactive choropleth map across all 7 quinquennial census rounds (1990–2020) and 4 demographic metrics (*Migrant Stock*, *Migrant Stock % of Population*, *5-Year Stock Change*, *5-Year Stock Growth %*).
3. **📈 Trends**: Long-term global aggregate trajectories and multi-country comparative time series.
4. **🏆 Rankings**: Dynamic leaderboards (Top 10 to Top 50) by migrant stock, demographic intensity, and growth.
5. **🔀 Route Explorer**: Top bilateral corridors and granular origin/destination filtered corridor analytics.
6. **🌎 Country Explorer**: Individual country profile with inbound origins, outbound diaspora destinations, and macroeconomic context.

### 🕸️ NETWORK ANALYSIS
7. **🕸️ Migration Network**: 2D force-directed and geographic network maps, centrality leaderboards (*Degree*, *Weighted Strength*, *Betweenness*, *PageRank*), and longitudinal graph metrics.
8. **🔗 Corridor Analysis**: Directional asymmetry analysis ($[-1, 1]$ index), reciprocal stock balances, origin concentration (HHI), and global top 50 corridors master table.
9. **🌐 Communities**: Modularity community detection discovering dense empirical clusters in the bilateral stock network.

### 📊 ADVANCED ANALYTICS (Phase 5)
10. **📊 Advanced Analytics**:
    - *Geographic Concentration (HHI)*: Destination and origin Herfindahl-Hirschman Indices across 1990–2020 with benchmark bands (<1,000 Unconcentrated, 1,000–1,800 Moderately Concentrated, >1,800 Highly Concentrated).
    - *Migration Change & Growth*: 5-year intercensal growth classification (*Strong Increase*, *Moderate Increase*, *Stable*, *Moderate Decrease*, *Strong Decrease*), fastest-growing destinations, and largest absolute stock adjustments.
    - *Socioeconomic Relationships*: Bivariate correlation engine (Pearson $r$, Spearman $\rho$, p-values) and interactive scatter plots with OLS trendlines.
    - *Outlier & Anomaly Detection*: Transparent IQR ($1.5 \times \text{IQR}$) and Z-Score ($|z| > 2.5$) anomaly detection with descriptive context.
11. **⚖️ Country Comparison**:
    - Multi-country selector (2–5 nations).
    - Absolute indicator comparison matrix across demographic, economic, and network dimensions.
    - Normalized relative comparison chart ($[0, 100]$ scale relative to global sovereign distribution).
    - Multi-line historical trajectories across 1990–2020.
12. **💡 Migration Insights**:
    - Automated, deterministic data storytelling engine generating human-readable narrative summaries across Global Trends, Concentration, Fastest Growth, Largest Changes, Major Corridors, Socioeconomic Associations, and Network Structure.
    - Full traceability to underlying dataframe calculations.

### ℹ️ INFORMATION
13. **ℹ️ Methodology**: Detailed documentation of UN DESA 2020 Revision, World Bank WDI datasets, mathematical formulations, and the strict **Migrant Stock $\neq$ Migration Flow** and **Correlation $\neq$ Causation** principles.
14. **⚙️ Settings**: Universal theme switcher (**☀️ Light Mode** / **🌙 Dark Mode**) and Streamlit cache manager.

---

## ⚠️ Critical Scientific Principles

### 1. Migrant Stock vs. Migration Flow
| Dimension | International Migrant Stock (This Dataset) | Migration Flow |
| :--- | :--- | :--- |
| **Definition** | Estimated number of foreign-born individuals residing in a destination country at a mid-year point in time. | Number of individuals moving across borders over a specific period (e.g. annual entries/exits). |
| **Measurement Unit** | People residing at time $t$ | Moves / events per year |
| **Components of Change** | Includes net immigration, deaths of migrants, return migration, naturalization, and census reclassifications. | Border crossing counts only. |
| **UN Revision** | Official 5-year census rounds (1990, 1995, 2000, 2005, 2010, 2015, 2020). | Administrative entry registers (UNHCR, OECD, national border registries). |

> [!IMPORTANT]
> **Intercensal stock changes are NOT annual migration flows.** Intercensal differences between 5-year rounds reflect net cumulative changes in the residing foreign-born population, not gross annual border crossings.

### 2. Observational Correlation vs. Causation
All cross-sectional bivariate relationships between macroeconomic context (GDP per capita, unemployment, population) and migrant stock describe observed statistical associations and do **NOT** establish causal migration drivers.

---

## 🗂️ Project Structure

```
global-migration-observatory/
│
├── app.py                      # 14-page interactive Streamlit application
├── run_pipeline.py             # Root runner script for end-to-end data pipeline
├── config.yaml                 # Central configuration for paths, indicators, and URLs
├── requirements.txt            # Python dependencies (isolated in .venv)
├── pytest.ini                  # Pytest configuration
├── README.md                   # Repository documentation
│
├── src/                        # Modular source code
│   ├── config.py               # YAML configuration loader
│   ├── data_loader.py          # Data ingestion & remote download helpers
│   ├── data_cleaning.py        # ISO-3 standardizer & data cleaning engine
│   ├── data_merging.py         # Merging country & bilateral datasets
│   ├── data_validation.py      # Automated 14-rule data quality validator
│   ├── feature_engineering.py  # Derived metrics (shares, growth, ranks)
│   ├── dashboard_data.py       # High-performance analytical query layer
│   ├── network_analysis.py     # NetworkX graph modeling, centrality, communities
│   ├── network_visualization.py# 2D, circular, and geographic network plots
│   ├── advanced_analytics.py   # HHI, correlations, outliers, change classifications
│   ├── insight_engine.py       # Deterministic rule-based data storytelling
│   ├── ui_theme.py             # Design system, Light/Dark tokens, reduced-motion
│   ├── ui_components.py        # Reusable UI cards, badges, and alerts
│   ├── pipeline.py             # End-to-end pipeline orchestrator
│   └── utils.py                # Logging and helper utilities
│
├── tests/                      # Automated unit & integration test suite (57 tests)
│   ├── test_data_loader.py
│   ├── test_data_cleaning.py
│   ├── test_data_validation.py
│   ├── test_feature_engineering.py
│   ├── test_dashboard_data.py
│   ├── test_network_analysis.py
│   ├── test_advanced_analytics.py
│   └── test_streamlit_pages.py
│
└── data/                       # Data directory
    ├── raw/                    # Raw UN DESA & World Bank datasets
    ├── processed/              # Verified CSV & Parquet processed datasets
    └── reports/                # Automated data quality validation reports
```

---

## 🚀 Quickstart & Execution

```powershell
# Navigate to the project root
cd "C:\Users\shrut\.gemini\antigravity\scratch\world_migration"

# Run the complete test suite (57/57 tests passing)
.venv\Scripts\pytest.exe -v

# Launch the Streamlit dashboard
.venv\Scripts\streamlit.exe run app.py
```
