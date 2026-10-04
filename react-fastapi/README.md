# 🌍 Global Migration Observatory — React/Vite Edition

> **Empirical analysis of international migrant stock dynamics (1990–2020), bilateral corridor networks, and socioeconomic interactions.**

This project is the **React + Vite Edition** of the Global Migration Observatory, featuring a modern decoupled full-stack architecture powered by a high-performance **FastAPI** backend and a reactive **React + Vite** frontend.

---

## 🏛 Architecture Overview

```
React / Vite (Frontend)
   │  (Port 5173 / Proxy)
   ▼
FastAPI (REST API Backend)
   │  (Port 8000 / JSON Responses)
   ▼
Scientific Python Analytics & Data Layer (NetworkX, Pandas, NumPy, Scipy)
   │  (In-Memory Cached DataFrames)
   ▼
UN DESA 2020 Revision & World Bank WDI Datasets (1990–2020)
```

---

## 🔬 Scientific Data & Methodological Principles

### 1. Migrant Stock Definition
**Migrant stock** is strictly defined as the estimated number of international migrants (foreign-born persons or foreign citizens) residing in a given destination country or territory at mid-year, as published in the official **UN DESA Population Division (2020 Revision)** dataset.
* It measures **accumulated population stock** over decades.
* It is **NOT** annual migration flow, border crossings, or yearly entry numbers.

### 2. Observation Census Rounds
The UN DESA empirical series contains exactly 7 observation rounds at 5-year intervals:
`1990, 1995, 2000, 2005, 2010, 2015, 2020`

### 3. World Bank Indicators
Coupled with mid-year demographic data across 1990–2020:
* `NY.GDP.MKTP.CD`: GDP (current US$)
* `NY.GDP.PCAP.CD`: GDP per capita (current US$)
* `SP.POP.TOTL`: Total population
* `SL.UEM.TOTL.ZS`: Total unemployment (% of total labor force)

### 4. Data Integrity Guarantee
* Zero synthetic migration, socioeconomic, corridor, or country data.
* Missing socioeconomic figures remain `null`/missing without interpolation or fabrication.

---

## 📁 Project Directory Structure

```
global-migration-observatory-react/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application with CORS & lifespan data loading
│   │   ├── config.py                # Backend configuration and constants
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py        # GET /api/health
│   │   │       ├── years.py         # GET /api/years
│   │   │       ├── countries.py     # GET /api/countries
│   │   │       └── overview.py      # GET /api/overview?year=2020
│   │   ├── services/
│   │   │   ├── data_service.py      # In-memory cached dataset access layer
│   │   │   ├── overview_service.py  # Overview KPI calculation service
│   │   │   └── countries_service.py # Sovereign & regional country metadata
│   │   └── schemas/
│   │       ├── health.py            # Pydantic schemas for /api/health
│   │       ├── years.py             # Pydantic schemas for /api/years
│   │       ├── countries.py         # Pydantic schemas for /api/countries
│   │       └── overview.py          # Pydantic schemas for /api/overview
│   ├── src/                         # Preserved scientific Python analytics layer
│   │   ├── config.py                # Data path resolvers
│   │   ├── data_loader.py           # UN DESA & World Bank data loaders
│   │   ├── data_cleaning.py         # Standardized cleaning and ISO3 normalization
│   │   ├── data_validation.py       # Strict schema & boundary checks
│   │   ├── data_merging.py          # Socioeconomic dataset joining
│   │   ├── feature_engineering.py   # Growth rate & density calculations
│   │   ├── dashboard_data.py        # High-performance KPI & aggregation queries
│   │   ├── network_analysis.py      # NetworkX graph modeling & community detection
│   │   ├── network_visualization.py # 2D/3D graph coordinate generation
│   │   ├── advanced_analytics.py    # Regressions, correlations, HHI, and IQR anomalies
│   │   ├── insight_engine.py        # Automated text narrative synthesis
│   │   └── utils.py                 # Number formatting and statistical helpers
│   ├── tests/                       # Complete backend unit and API test suite
│   ├── requirements.txt             # Python backend dependencies
│   └── pytest.ini                   # Pytest configuration
│
├── frontend/
│   ├── src/
│   │   ├── components/              # Header, Sidebar, YearSelector, StatusBadge, Card
│   │   ├── pages/                   # 14 observatory route page components
│   │   ├── layouts/                 # MainLayout shell
│   │   ├── services/api.js          # Centralized API query functions
│   │   ├── context/AppContext.jsx   # Global state management
│   │   ├── hooks/useAppContext.js   # Custom context hook
│   │   ├── styles/index.css         # Universal design system & CSS tokens
│   │   ├── App.jsx                  # Root router and component view switcher
│   │   └── main.jsx                 # Vite mount point
│   ├── public/                      # Static assets & favicon
│   ├── package.json                 # Frontend dependencies & scripts
│   ├── vite.config.js               # Vite configuration with /api proxy
│   └── index.html                   # Semantic HTML5 entrypoint
│
├── data/                            # Processed and raw datasets
│   ├── processed/
│   ├── raw/
│   └── reports/
├── README.md                        # Documentation
└── .gitignore                       # Git ignore configuration
```

---

## 🚀 Getting Started

### 1. Backend Setup (FastAPI)

```bash
cd global-migration-observatory-react

# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate (macOS/Linux)

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Run automated tests
pytest backend/tests -v

# 4. Start the FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```

The interactive API documentation is available at:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Frontend Setup (React + Vite)

```bash
cd global-migration-observatory-react/frontend

# 1. Install frontend dependencies
npm install

# 2. Start the Vite development server
npm run dev
```

The React frontend will be running at:
* Application UI: [http://localhost:5173](http://localhost:5173)

---

## 📡 API Endpoints Implemented in Phase 1

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check returning service status and edition |
| `GET` | `/api/years` | Returns the 7 official UN DESA observation years |
| `GET` | `/api/countries` | Returns recognized sovereign nations and regional entities |
| `GET` | `/api/overview?year=2020` | Returns live calculated executive KPIs for target year |

---

## 🧪 Testing

To execute all 68 backend regression and API endpoint tests:

```bash
cd global-migration-observatory-react
.venv\Scripts\pytest.exe backend/tests -v
```

Expected result: **68 passed, 0 failures, 0 errors**.
