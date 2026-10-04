# Global Migration Observatory - Data Quality & Validation Report

**Phase**: Phase 1 Foundation & Data Ingestion  
**Status**: ✅ ALL CHECKS PASSED  
**Summary**: 14/14 validation checks passed.  

---

## 1. Dataset Dimensions & Coverage

| dataset_name                         | total_rows | total_columns | unique_countries | min_year | max_year | years_covered                                                                                                                                                                            | missing_migrant_stock_count | missing_migrant_stock_pct | missing_gdp_count | missing_gdp_pct | missing_gdp_per_capita_count | missing_gdp_per_capita_pct | missing_population_count | missing_population_pct | missing_unemployment_count | missing_unemployment_pct |
|--------------------------------------|------------|---------------|------------------|----------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|---------------------------|-------------------|-----------------|------------------------------|----------------------------|--------------------------|------------------------|----------------------------|--------------------------|
| UN DESA Destination Migrant Stock    | 1981       | 11            | 233              | 1990     | 2020     | 1990, 1995, 2000, 2005, 2010, 2015, 2020                                                                                                                                                 | 36.0                        | 1.82                      |                   |                 |                              |                            |                          |                        |                            |                          |
| UN DESA Bilateral Migrant Stock      | 259357     | 9             | 233              | 1990     | 2020     | 1990, 1995, 2000, 2005, 2010, 2015, 2020                                                                                                                                                 | 0.0                         | 0.0                       |                   |                 |                              |                            |                          |                        |                            |                          |
| World Bank Socioeconomic Indicators  | 7998       | 9             | 258              | 1990     | 2020     | 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020 |                             |                           | 326.0             | 4.08            | 326.0                        | 4.08                       | 0.0                      | 0.0                    | 1158.0                     | 14.48                    |
| Merged Country Socioeconomic Dataset | 1505       | 15            | 215              | 1990     | 2020     | 1990, 1995, 2000, 2005, 2010, 2015, 2020                                                                                                                                                 | 22.0                        | 1.46                      | 74.0              | 4.92            | 74.0                         | 4.92                       | 0.0                      | 0.0                    | 389.0                      | 25.85                    |

---

## 2. Validation Check Results

| dataset_name                         | check_name                               | status | severity | details                                                                                                                       |
|--------------------------------------|------------------------------------------|--------|----------|-------------------------------------------------------------------------------------------------------------------------------|
| UN DESA Destination Migrant Stock    | Required Columns Exist                   | PASS   | ERROR    | All required columns present.                                                                                                 |
| UN DESA Destination Migrant Stock    | Valid Year Range                         | PASS   | ERROR    | Valid years: [np.int64(1990), np.int64(1995), np.int64(2000), np.int64(2005), np.int64(2010), np.int64(2015), np.int64(2020)] |
| UN DESA Destination Migrant Stock    | Sovereign ISO3 Country Codes             | PASS   | ERROR    | All sovereign country codes are valid ISO3.                                                                                   |
| UN DESA Destination Migrant Stock    | Non-Negative Migrant Stock               | PASS   | ERROR    | All migrant stock values are non-negative.                                                                                    |
| UN DESA Destination Migrant Stock    | Unique Primary Key (country_code, year)  | PASS   | ERROR    | Primary keys are unique.                                                                                                      |
| UN DESA Bilateral Migrant Stock      | Required Columns Exist                   | PASS   | ERROR    | All required columns present.                                                                                                 |
| UN DESA Bilateral Migrant Stock      | Non-Negative Migrant Stock               | PASS   | ERROR    | All bilateral migrant stock values are non-negative.                                                                          |
| UN DESA Bilateral Migrant Stock      | Unique Corridor Key (origin, dest, year) | PASS   | ERROR    | Corridor primary keys are unique.                                                                                             |
| World Bank Socioeconomic Indicators  | Required Columns Exist                   | PASS   | ERROR    | All indicator columns present.                                                                                                |
| World Bank Socioeconomic Indicators  | Non-Negative Population & GDP/Capita     | PASS   | ERROR    | Values are strictly non-negative.                                                                                             |
| World Bank Socioeconomic Indicators  | Unemployment Percentage Range [0-100%]   | PASS   | ERROR    | All unemployment rates within 0-100%.                                                                                         |
| World Bank Socioeconomic Indicators  | Unique Primary Key (country_code, year)  | PASS   | ERROR    | Primary keys are unique.                                                                                                      |
| Merged Country Socioeconomic Dataset | Required Merged Columns Exist            | PASS   | ERROR    | All merged fields present.                                                                                                    |
| Merged Country Socioeconomic Dataset | Migration & Population Overlap           | PASS   | ERROR    | 1,483 records have both migrant stock and population.                                                                         |

---

## 3. Data Integrity & Methodological Notes

- **Migrant Stock vs Flow**: Migrant stock represents the estimated number of foreign-born / foreign citizens residing in a country at mid-year. It is **NOT** annual migration flow.
- **Zero Fabrication**: No values were synthetically generated, imputed arbitrarily, or replaced with placeholders.
- **Aggregates Handling**: Regional and income group aggregates are cleanly categorized and flagged (`is_aggregate`) to prevent distorting sovereign country comparisons.
- **Country Resolution**: ISO 3166-1 alpha-3 codes are enforced as the primary merge key across UN DESA and World Bank sources.
