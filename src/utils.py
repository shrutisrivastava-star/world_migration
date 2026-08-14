"""
Utility module for standardizing country names, ISO codes, and entity classifications.
Provides reference mappings across UN DESA, World Bank, and ISO-3166-1 standards.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd


# Canonical ISO 3166-1 alpha-3, numeric M49, and standard name mappings
# Includes sovereign nations, territories, and recognized entities
ISO_COUNTRY_DATABASE = [
    {"name": "Afghanistan", "iso3": "AFG", "iso2": "AF", "m49": 4, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Albania", "iso3": "ALB", "iso2": "AL", "m49": 8, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Algeria", "iso3": "DZA", "iso2": "DZ", "m49": 12, "entity_type": "country", "region": "Northern Africa"},
    {"name": "American Samoa", "iso3": "ASM", "iso2": "AS", "m49": 16, "entity_type": "territory", "region": "Polynesia"},
    {"name": "Andorra", "iso3": "AND", "iso2": "AD", "m49": 20, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Angola", "iso3": "AGO", "iso2": "AO", "m49": 24, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Anguilla", "iso3": "AIA", "iso2": "AI", "m49": 660, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Antigua and Barbuda", "iso3": "ATG", "iso2": "AG", "m49": 28, "entity_type": "country", "region": "Caribbean"},
    {"name": "Argentina", "iso3": "ARG", "iso2": "AR", "m49": 32, "entity_type": "country", "region": "South America"},
    {"name": "Armenia", "iso3": "ARM", "iso2": "AM", "m49": 51, "entity_type": "country", "region": "Western Asia"},
    {"name": "Aruba", "iso3": "ABW", "iso2": "AW", "m49": 533, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Australia", "iso3": "AUS", "iso2": "AU", "m49": 36, "entity_type": "country", "region": "Australia and New Zealand"},
    {"name": "Austria", "iso3": "AUT", "iso2": "AT", "m49": 40, "entity_type": "country", "region": "Western Europe"},
    {"name": "Azerbaijan", "iso3": "AZE", "iso2": "AZ", "m49": 31, "entity_type": "country", "region": "Western Asia"},
    {"name": "Bahamas", "iso3": "BHS", "iso2": "BS", "m49": 44, "entity_type": "country", "region": "Caribbean"},
    {"name": "Bahrain", "iso3": "BHR", "iso2": "BH", "m49": 48, "entity_type": "country", "region": "Western Asia"},
    {"name": "Bangladesh", "iso3": "BGD", "iso2": "BD", "m49": 50, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Barbados", "iso3": "BRB", "iso2": "BB", "m49": 52, "entity_type": "country", "region": "Caribbean"},
    {"name": "Belarus", "iso3": "BLR", "iso2": "BY", "m49": 112, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Belgium", "iso3": "BEL", "iso2": "BE", "m49": 56, "entity_type": "country", "region": "Western Europe"},
    {"name": "Belize", "iso3": "BLZ", "iso2": "BZ", "m49": 84, "entity_type": "country", "region": "Central America"},
    {"name": "Benin", "iso3": "BEN", "iso2": "BJ", "m49": 204, "entity_type": "country", "region": "Western Africa"},
    {"name": "Bermuda", "iso3": "BMU", "iso2": "BM", "m49": 60, "entity_type": "territory", "region": "Northern America"},
    {"name": "Bhutan", "iso3": "BTN", "iso2": "BT", "m49": 64, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Bolivia (Plurinational State of)", "iso3": "BOL", "iso2": "BO", "m49": 68, "entity_type": "country", "region": "South America"},
    {"name": "Bosnia and Herzegovina", "iso3": "BIH", "iso2": "BA", "m49": 70, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Botswana", "iso3": "BWA", "iso2": "BW", "m49": 72, "entity_type": "country", "region": "Southern Africa"},
    {"name": "Brazil", "iso3": "BRA", "iso2": "BR", "m49": 76, "entity_type": "country", "region": "South America"},
    {"name": "British Virgin Islands", "iso3": "VGB", "iso2": "VG", "m49": 92, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Brunei Darussalam", "iso3": "BRN", "iso2": "BN", "m49": 96, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Bulgaria", "iso3": "BGR", "iso2": "BG", "m49": 100, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Burkina Faso", "iso3": "BFA", "iso2": "BF", "m49": 854, "entity_type": "country", "region": "Western Africa"},
    {"name": "Burundi", "iso3": "BDI", "iso2": "BI", "m49": 108, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Cabo Verde", "iso3": "CPV", "iso2": "CV", "m49": 132, "entity_type": "country", "region": "Western Africa"},
    {"name": "Cambodia", "iso3": "KHM", "iso2": "KH", "m49": 116, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Cameroon", "iso3": "CMR", "iso2": "CM", "m49": 120, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Canada", "iso3": "CAN", "iso2": "CA", "m49": 124, "entity_type": "country", "region": "Northern America"},
    {"name": "Cayman Islands", "iso3": "CYM", "iso2": "KY", "m49": 136, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Central African Republic", "iso3": "CAF", "iso2": "CF", "m49": 140, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Chad", "iso3": "TCD", "iso2": "TD", "m49": 148, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Chile", "iso3": "CHL", "iso2": "CL", "m49": 152, "entity_type": "country", "region": "South America"},
    {"name": "China", "iso3": "CHN", "iso2": "CN", "m49": 156, "entity_type": "country", "region": "Eastern Asia"},
    {"name": "China, Hong Kong SAR", "iso3": "HKG", "iso2": "HK", "m49": 344, "entity_type": "territory", "region": "Eastern Asia"},
    {"name": "China, Macao SAR", "iso3": "MAC", "iso2": "MO", "m49": 446, "entity_type": "territory", "region": "Eastern Asia"},
    {"name": "Colombia", "iso3": "COL", "iso2": "CO", "m49": 170, "entity_type": "country", "region": "South America"},
    {"name": "Comoros", "iso3": "COM", "iso2": "KM", "m49": 174, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Congo", "iso3": "COG", "iso2": "CG", "m49": 178, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Cook Islands", "iso3": "COK", "iso2": "CK", "m49": 184, "entity_type": "territory", "region": "Polynesia"},
    {"name": "Costa Rica", "iso3": "CRI", "iso2": "CR", "m49": 188, "entity_type": "country", "region": "Central America"},
    {"name": "Côte d'Ivoire", "iso3": "CIV", "iso2": "CI", "m49": 384, "entity_type": "country", "region": "Western Africa"},
    {"name": "Croatia", "iso3": "HRV", "iso2": "HR", "m49": 191, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Cuba", "iso3": "CUB", "iso2": "CU", "m49": 192, "entity_type": "country", "region": "Caribbean"},
    {"name": "Curaçao", "iso3": "CUW", "iso2": "CW", "m49": 531, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Cyprus", "iso3": "CYP", "iso2": "CY", "m49": 196, "entity_type": "country", "region": "Western Asia"},
    {"name": "Czechia", "iso3": "CZE", "iso2": "CZ", "m49": 203, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Democratic People's Republic of Korea", "iso3": "PRK", "iso2": "KP", "m49": 408, "entity_type": "country", "region": "Eastern Asia"},
    {"name": "Democratic Republic of the Congo", "iso3": "COD", "iso2": "CD", "m49": 180, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Denmark", "iso3": "DNK", "iso2": "DK", "m49": 208, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Djibouti", "iso3": "DJI", "iso2": "DJ", "m49": 262, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Dominica", "iso3": "DMA", "iso2": "DM", "m49": 212, "entity_type": "country", "region": "Caribbean"},
    {"name": "Dominican Republic", "iso3": "DOM", "iso2": "DO", "m49": 214, "entity_type": "country", "region": "Caribbean"},
    {"name": "Ecuador", "iso3": "ECU", "iso2": "EC", "m49": 218, "entity_type": "country", "region": "South America"},
    {"name": "Egypt", "iso3": "EGY", "iso2": "EG", "m49": 818, "entity_type": "country", "region": "Northern Africa"},
    {"name": "El Salvador", "iso3": "SLV", "iso2": "SV", "m49": 222, "entity_type": "country", "region": "Central America"},
    {"name": "Equatorial Guinea", "iso3": "GNQ", "iso2": "GQ", "m49": 226, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Eritrea", "iso3": "ERI", "iso2": "ER", "m49": 232, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Estonia", "iso3": "EST", "iso2": "EE", "m49": 233, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Eswatini", "iso3": "SWZ", "iso2": "SZ", "m49": 748, "entity_type": "country", "region": "Southern Africa"},
    {"name": "Ethiopia", "iso3": "ETH", "iso2": "ET", "m49": 231, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Faeroe Islands", "iso3": "FRO", "iso2": "FO", "m49": 234, "entity_type": "territory", "region": "Northern Europe"},
    {"name": "Falkland Islands (Malvinas)", "iso3": "FLK", "iso2": "FK", "m49": 238, "entity_type": "territory", "region": "South America"},
    {"name": "Fiji", "iso3": "FJI", "iso2": "FJ", "m49": 242, "entity_type": "country", "region": "Melanesia"},
    {"name": "Finland", "iso3": "FIN", "iso2": "FI", "m49": 246, "entity_type": "country", "region": "Northern Europe"},
    {"name": "France", "iso3": "FRA", "iso2": "FR", "m49": 250, "entity_type": "country", "region": "Western Europe"},
    {"name": "French Guiana", "iso3": "GUF", "iso2": "GF", "m49": 254, "entity_type": "territory", "region": "South America"},
    {"name": "French Polynesia", "iso3": "PYF", "iso2": "PF", "m49": 258, "entity_type": "territory", "region": "Polynesia"},
    {"name": "Gabon", "iso3": "GAB", "iso2": "GA", "m49": 266, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Gambia", "iso3": "GMB", "iso2": "GM", "m49": 270, "entity_type": "country", "region": "Western Africa"},
    {"name": "Georgia", "iso3": "GEO", "iso2": "GE", "m49": 268, "entity_type": "country", "region": "Western Asia"},
    {"name": "Germany", "iso3": "DEU", "iso2": "DE", "m49": 276, "entity_type": "country", "region": "Western Europe"},
    {"name": "Ghana", "iso3": "GHA", "iso2": "GH", "m49": 288, "entity_type": "country", "region": "Western Africa"},
    {"name": "Gibraltar", "iso3": "GIB", "iso2": "GI", "m49": 292, "entity_type": "territory", "region": "Southern Europe"},
    {"name": "Greece", "iso3": "GRC", "iso2": "GR", "m49": 300, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Greenland", "iso3": "GRL", "iso2": "GL", "m49": 304, "entity_type": "territory", "region": "Northern America"},
    {"name": "Grenada", "iso3": "GRD", "iso2": "GD", "m49": 308, "entity_type": "country", "region": "Caribbean"},
    {"name": "Guadeloupe", "iso3": "GLP", "iso2": "GP", "m49": 312, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Guam", "iso3": "GUM", "iso2": "GU", "m49": 316, "entity_type": "territory", "region": "Micronesia"},
    {"name": "Guatemala", "iso3": "GTM", "iso2": "GT", "m49": 320, "entity_type": "country", "region": "Central America"},
    {"name": "Guinea", "iso3": "GIN", "iso2": "GN", "m49": 324, "entity_type": "country", "region": "Western Africa"},
    {"name": "Guinea-Bissau", "iso3": "GNB", "iso2": "GW", "m49": 624, "entity_type": "country", "region": "Western Africa"},
    {"name": "Guyana", "iso3": "GUY", "iso2": "GY", "m49": 328, "entity_type": "country", "region": "South America"},
    {"name": "Haiti", "iso3": "HTI", "iso2": "HT", "m49": 332, "entity_type": "country", "region": "Caribbean"},
    {"name": "Holy See", "iso3": "VAT", "iso2": "VA", "m49": 336, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Honduras", "iso3": "HND", "iso2": "HN", "m49": 340, "entity_type": "country", "region": "Central America"},
    {"name": "Hungary", "iso3": "HUN", "iso2": "HU", "m49": 348, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Iceland", "iso3": "ISL", "iso2": "IS", "m49": 352, "entity_type": "country", "region": "Northern Europe"},
    {"name": "India", "iso3": "IND", "iso2": "IN", "m49": 356, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Indonesia", "iso3": "IDN", "iso2": "ID", "m49": 360, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Iran (Islamic Republic of)", "iso3": "IRN", "iso2": "IR", "m49": 364, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Iraq", "iso3": "IRQ", "iso2": "IQ", "m49": 368, "entity_type": "country", "region": "Western Asia"},
    {"name": "Ireland", "iso3": "IRL", "iso2": "IE", "m49": 372, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Isle of Man", "iso3": "IMN", "iso2": "IM", "m49": 833, "entity_type": "territory", "region": "Northern Europe"},
    {"name": "Israel", "iso3": "ISR", "iso2": "IL", "m49": 376, "entity_type": "country", "region": "Western Asia"},
    {"name": "Italy", "iso3": "ITA", "iso2": "IT", "m49": 380, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Jamaica", "iso3": "JAM", "iso2": "JM", "m49": 388, "entity_type": "country", "region": "Caribbean"},
    {"name": "Japan", "iso3": "JPN", "iso2": "JP", "m49": 392, "entity_type": "country", "region": "Eastern Asia"},
    {"name": "Jordan", "iso3": "JOR", "iso2": "JO", "m49": 400, "entity_type": "country", "region": "Western Asia"},
    {"name": "Kazakhstan", "iso3": "KAZ", "iso2": "KZ", "m49": 398, "entity_type": "country", "region": "Central Asia"},
    {"name": "Kenya", "iso3": "KEN", "iso2": "KE", "m49": 404, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Kiribati", "iso3": "KIR", "iso2": "KI", "m49": 296, "entity_type": "country", "region": "Micronesia"},
    {"name": "Kuwait", "iso3": "KWT", "iso2": "KW", "m49": 414, "entity_type": "country", "region": "Western Asia"},
    {"name": "Kyrgyzstan", "iso3": "KGZ", "iso2": "KG", "m49": 417, "entity_type": "country", "region": "Central Asia"},
    {"name": "Lao People's Democratic Republic", "iso3": "LAO", "iso2": "LA", "m49": 418, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Latvia", "iso3": "LVA", "iso2": "LV", "m49": 428, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Lebanon", "iso3": "LBN", "iso2": "LB", "m49": 422, "entity_type": "country", "region": "Western Asia"},
    {"name": "Lesotho", "iso3": "LSO", "iso2": "LS", "m49": 426, "entity_type": "country", "region": "Southern Africa"},
    {"name": "Liberia", "iso3": "LBR", "iso2": "LR", "m49": 430, "entity_type": "country", "region": "Western Africa"},
    {"name": "Libya", "iso3": "LBY", "iso2": "LY", "m49": 434, "entity_type": "country", "region": "Northern Africa"},
    {"name": "Liechtenstein", "iso3": "LIE", "iso2": "LI", "m49": 438, "entity_type": "country", "region": "Western Europe"},
    {"name": "Lithuania", "iso3": "LTU", "iso2": "LT", "m49": 440, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Luxembourg", "iso3": "LUX", "iso2": "LU", "m49": 442, "entity_type": "country", "region": "Western Europe"},
    {"name": "Madagascar", "iso3": "MDG", "iso2": "MG", "m49": 450, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Malawi", "iso3": "MWI", "iso2": "MW", "m49": 454, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Malaysia", "iso3": "MYS", "iso2": "MY", "m49": 458, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Maldives", "iso3": "MDV", "iso2": "MV", "m49": 462, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Mali", "iso3": "MLI", "iso2": "ML", "m49": 466, "entity_type": "country", "region": "Western Africa"},
    {"name": "Malta", "iso3": "MLT", "iso2": "MT", "m49": 470, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Marshall Islands", "iso3": "MHL", "iso2": "MH", "m49": 584, "entity_type": "country", "region": "Micronesia"},
    {"name": "Martinique", "iso3": "MTQ", "iso2": "MQ", "m49": 474, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Mauritania", "iso3": "MRT", "iso2": "MR", "m49": 478, "entity_type": "country", "region": "Western Africa"},
    {"name": "Mauritius", "iso3": "MUS", "iso2": "MU", "m49": 480, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Mayotte", "iso3": "MYT", "iso2": "YT", "m49": 175, "entity_type": "territory", "region": "Eastern Africa"},
    {"name": "Mexico", "iso3": "MEX", "iso2": "MX", "m49": 484, "entity_type": "country", "region": "Central America"},
    {"name": "Micronesia (Fed. States of)", "iso3": "FSM", "iso2": "FM", "m49": 583, "entity_type": "country", "region": "Micronesia"},
    {"name": "Monaco", "iso3": "MCO", "iso2": "MC", "m49": 492, "entity_type": "country", "region": "Western Europe"},
    {"name": "Mongolia", "iso3": "MNG", "iso2": "MN", "m49": 496, "entity_type": "country", "region": "Eastern Asia"},
    {"name": "Montenegro", "iso3": "MNE", "iso2": "ME", "m49": 499, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Montserrat", "iso3": "MSR", "iso2": "MS", "m49": 500, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Morocco", "iso3": "MAR", "iso2": "MA", "m49": 504, "entity_type": "country", "region": "Northern Africa"},
    {"name": "Mozambique", "iso3": "MOZ", "iso2": "MZ", "m49": 508, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Myanmar", "iso3": "MMR", "iso2": "MM", "m49": 104, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Namibia", "iso3": "NAM", "iso2": "NA", "m49": 516, "entity_type": "country", "region": "Southern Africa"},
    {"name": "Nauru", "iso3": "NRU", "iso2": "NR", "m49": 520, "entity_type": "country", "region": "Micronesia"},
    {"name": "Nepal", "iso3": "NPL", "iso2": "NP", "m49": 524, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Netherlands", "iso3": "NLD", "iso2": "NL", "m49": 528, "entity_type": "country", "region": "Western Europe"},
    {"name": "New Caledonia", "iso3": "NCL", "iso2": "NC", "m49": 540, "entity_type": "territory", "region": "Melanesia"},
    {"name": "New Zealand", "iso3": "NZL", "iso2": "NZ", "m49": 554, "entity_type": "country", "region": "Australia and New Zealand"},
    {"name": "Nicaragua", "iso3": "NIC", "iso2": "NI", "m49": 558, "entity_type": "country", "region": "Central America"},
    {"name": "Niger", "iso3": "NER", "iso2": "NE", "m49": 562, "entity_type": "country", "region": "Western Africa"},
    {"name": "Nigeria", "iso3": "NGA", "iso2": "NG", "m49": 566, "entity_type": "country", "region": "Western Africa"},
    {"name": "Niue", "iso3": "NIU", "iso2": "NU", "m49": 570, "entity_type": "territory", "region": "Polynesia"},
    {"name": "North Macedonia", "iso3": "MKD", "iso2": "MK", "m49": 807, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Northern Mariana Islands", "iso3": "MNP", "iso2": "MP", "m49": 580, "entity_type": "territory", "region": "Micronesia"},
    {"name": "Norway", "iso3": "NOR", "iso2": "NO", "m49": 578, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Oman", "iso3": "OMN", "iso2": "OM", "m49": 512, "entity_type": "country", "region": "Western Asia"},
    {"name": "Pakistan", "iso3": "PAK", "iso2": "PK", "m49": 586, "entity_type": "country", "region": "Southern Asia"},
    {"name": "Palau", "iso3": "PLW", "iso2": "PW", "m49": 585, "entity_type": "country", "region": "Micronesia"},
    {"name": "Panama", "iso3": "PAN", "iso2": "PA", "m49": 591, "entity_type": "country", "region": "Central America"},
    {"name": "Papua New Guinea", "iso3": "PNG", "iso2": "PG", "m49": 598, "entity_type": "country", "region": "Melanesia"},
    {"name": "Paraguay", "iso3": "PRY", "iso2": "PY", "m49": 600, "entity_type": "country", "region": "South America"},
    {"name": "Peru", "iso3": "PER", "iso2": "PE", "m49": 604, "entity_type": "country", "region": "South America"},
    {"name": "Philippines", "iso3": "PHL", "iso2": "PH", "m49": 608, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Poland", "iso3": "POL", "iso2": "PL", "m49": 616, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Portugal", "iso3": "PRT", "iso2": "PT", "m49": 620, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Puerto Rico", "iso3": "PRI", "iso2": "PR", "m49": 630, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Qatar", "iso3": "QAT", "iso2": "QA", "m49": 634, "entity_type": "country", "region": "Western Asia"},
    {"name": "Republic of Korea", "iso3": "KOR", "iso2": "KR", "m49": 410, "entity_type": "country", "region": "Eastern Asia"},
    {"name": "Republic of Moldova", "iso3": "MDA", "iso2": "MD", "m49": 498, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Réunion", "iso3": "REU", "iso2": "RE", "m49": 638, "entity_type": "territory", "region": "Eastern Africa"},
    {"name": "Romania", "iso3": "ROU", "iso2": "RO", "m49": 642, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Russian Federation", "iso3": "RUS", "iso2": "RU", "m49": 643, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Rwanda", "iso3": "RWA", "iso2": "RW", "m49": 646, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Saint Helena", "iso3": "SHN", "iso2": "SH", "m49": 654, "entity_type": "territory", "region": "Western Africa"},
    {"name": "Saint Kitts and Nevis", "iso3": "KNA", "iso2": "KN", "m49": 659, "entity_type": "country", "region": "Caribbean"},
    {"name": "Saint Lucia", "iso3": "LCA", "iso2": "LC", "m49": 662, "entity_type": "country", "region": "Caribbean"},
    {"name": "Saint Pierre and Miquelon", "iso3": "SPM", "iso2": "PM", "m49": 666, "entity_type": "territory", "region": "Northern America"},
    {"name": "Saint Vincent and the Grenadines", "iso3": "VCT", "iso2": "VC", "m49": 670, "entity_type": "country", "region": "Caribbean"},
    {"name": "Samoa", "iso3": "WSM", "iso2": "WS", "m49": 882, "entity_type": "country", "region": "Polynesia"},
    {"name": "San Marino", "iso3": "SMR", "iso2": "SM", "m49": 674, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Sao Tome and Principe", "iso3": "STP", "iso2": "ST", "m49": 678, "entity_type": "country", "region": "Middle Africa"},
    {"name": "Saudi Arabia", "iso3": "SAU", "iso2": "SA", "m49": 682, "entity_type": "country", "region": "Western Asia"},
    {"name": "Senegal", "iso3": "SEN", "iso2": "SN", "m49": 686, "entity_type": "country", "region": "Western Africa"},
    {"name": "Serbia", "iso3": "SRB", "iso2": "RS", "m49": 688, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Seychelles", "iso3": "SYC", "iso2": "SC", "m49": 690, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Sierra Leone", "iso3": "SLE", "iso2": "SL", "m49": 694, "entity_type": "country", "region": "Western Africa"},
    {"name": "Singapore", "iso3": "SGP", "iso2": "SG", "m49": 702, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Sint Maarten (Dutch part)", "iso3": "SXM", "iso2": "SX", "m49": 534, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Slovakia", "iso3": "SVK", "iso2": "SK", "m49": 703, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "Slovenia", "iso3": "SVN", "iso2": "SI", "m49": 705, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Solomon Islands", "iso3": "SLB", "iso2": "SB", "m49": 90, "entity_type": "country", "region": "Melanesia"},
    {"name": "Somalia", "iso3": "SOM", "iso2": "SO", "m49": 706, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "South Africa", "iso3": "ZAF", "iso2": "ZA", "m49": 710, "entity_type": "country", "region": "Southern Africa"},
    {"name": "South Sudan", "iso3": "SSD", "iso2": "SS", "m49": 728, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Spain", "iso3": "ESP", "iso2": "ES", "m49": 724, "entity_type": "country", "region": "Southern Europe"},
    {"name": "Sri Lanka", "iso3": "LKA", "iso2": "LK", "m49": 144, "entity_type": "country", "region": "Southern Asia"},
    {"name": "State of Palestine", "iso3": "PSE", "iso2": "PS", "m49": 275, "entity_type": "country", "region": "Western Asia"},
    {"name": "Sudan", "iso3": "SDN", "iso2": "SD", "m49": 729, "entity_type": "country", "region": "Northern Africa"},
    {"name": "Suriname", "iso3": "SUR", "iso2": "SR", "m49": 740, "entity_type": "country", "region": "South America"},
    {"name": "Sweden", "iso3": "SWE", "iso2": "SE", "m49": 752, "entity_type": "country", "region": "Northern Europe"},
    {"name": "Switzerland", "iso3": "CHE", "iso2": "CH", "m49": 756, "entity_type": "country", "region": "Western Europe"},
    {"name": "Syrian Arab Republic", "iso3": "SYR", "iso2": "SY", "m49": 760, "entity_type": "country", "region": "Western Asia"},
    {"name": "Tajikistan", "iso3": "TJK", "iso2": "TJ", "m49": 762, "entity_type": "country", "region": "Central Asia"},
    {"name": "Thailand", "iso3": "THA", "iso2": "TH", "m49": 764, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Timor-Leste", "iso3": "TLS", "iso2": "TL", "m49": 626, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Togo", "iso3": "TGO", "iso2": "TG", "m49": 768, "entity_type": "country", "region": "Western Africa"},
    {"name": "Tokelau", "iso3": "TKL", "iso2": "TK", "m49": 772, "entity_type": "territory", "region": "Polynesia"},
    {"name": "Tonga", "iso3": "TON", "iso2": "TO", "m49": 776, "entity_type": "country", "region": "Polynesia"},
    {"name": "Trinidad and Tobago", "iso3": "TTO", "iso2": "TT", "m49": 780, "entity_type": "country", "region": "Caribbean"},
    {"name": "Tunisia", "iso3": "TUN", "iso2": "TN", "m49": 788, "entity_type": "country", "region": "Northern Africa"},
    {"name": "Türkiye", "iso3": "TUR", "iso2": "TR", "m49": 792, "entity_type": "country", "region": "Western Asia"},
    {"name": "Turkmenistan", "iso3": "TKM", "iso2": "TM", "m49": 795, "entity_type": "country", "region": "Central Asia"},
    {"name": "Turks and Caicos Islands", "iso3": "TCA", "iso2": "TC", "m49": 796, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Tuvalu", "iso3": "TUV", "iso2": "TV", "m49": 798, "entity_type": "country", "region": "Polynesia"},
    {"name": "Uganda", "iso3": "UGA", "iso2": "UG", "m49": 800, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Ukraine", "iso3": "UKR", "iso2": "UA", "m49": 804, "entity_type": "country", "region": "Eastern Europe"},
    {"name": "United Arab Emirates", "iso3": "ARE", "iso2": "AE", "m49": 784, "entity_type": "country", "region": "Western Asia"},
    {"name": "United Kingdom", "iso3": "GBR", "iso2": "GB", "m49": 826, "entity_type": "country", "region": "Northern Europe"},
    {"name": "United Republic of Tanzania", "iso3": "TZA", "iso2": "TZ", "m49": 834, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "United States of America", "iso3": "USA", "iso2": "US", "m49": 840, "entity_type": "country", "region": "Northern America"},
    {"name": "United States Virgin Islands", "iso3": "VIR", "iso2": "VI", "m49": 850, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Uruguay", "iso3": "URY", "iso2": "UY", "m49": 858, "entity_type": "country", "region": "South America"},
    {"name": "Uzbekistan", "iso3": "UZB", "iso2": "UZ", "m49": 860, "entity_type": "country", "region": "Central Asia"},
    {"name": "Vanuatu", "iso3": "VUT", "iso2": "VU", "m49": 548, "entity_type": "country", "region": "Melanesia"},
    {"name": "Venezuela (Bolivarian Republic of)", "iso3": "VEN", "iso2": "VE", "m49": 862, "entity_type": "country", "region": "South America"},
    {"name": "Viet Nam", "iso3": "VNM", "iso2": "VN", "m49": 704, "entity_type": "country", "region": "South-Eastern Asia"},
    {"name": "Wallis and Futuna Islands", "iso3": "WLF", "iso2": "WF", "m49": 876, "entity_type": "territory", "region": "Polynesia"},
    {"name": "Bonaire, Sint Eustatius and Saba", "iso3": "BES", "iso2": "BQ", "m49": 535, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Saint Barthélemy", "iso3": "BLM", "iso2": "BL", "m49": 652, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Saint Martin (French part)", "iso3": "MAF", "iso2": "MF", "m49": 663, "entity_type": "territory", "region": "Caribbean"},
    {"name": "Western Sahara", "iso3": "ESH", "iso2": "EH", "m49": 732, "entity_type": "territory", "region": "Northern Africa"},
    {"name": "Yemen", "iso3": "YEM", "iso2": "YE", "m49": 887, "entity_type": "country", "region": "Western Asia"},
    {"name": "Zambia", "iso3": "ZMB", "iso2": "ZM", "m49": 894, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Zimbabwe", "iso3": "ZWE", "iso2": "ZW", "m49": 716, "entity_type": "country", "region": "Eastern Africa"},
    {"name": "Kosovo", "iso3": "XKX", "iso2": "XK", "m49": 999, "entity_type": "territory", "region": "Southern Europe"},
]

# UN M49 Regional and Development Aggregates
UN_M49_AGGREGATE_CODES = {
    1: {"name": "World", "type": "world"},
    2: {"name": "Africa", "type": "region"},
    9: {"name": "Oceania", "type": "region"},
    19: {"name": "Americas", "type": "region"},
    142: {"name": "Asia", "type": "region"},
    150: {"name": "Europe", "type": "region"},
    419: {"name": "Latin America and the Caribbean", "type": "region"},
    900: {"name": "World", "type": "world"},
    901: {"name": "More developed regions", "type": "aggregate"},
    902: {"name": "Less developed regions", "type": "aggregate"},
    903: {"name": "Latin America and the Caribbean", "type": "region"},
    904: {"name": "Latin America and the Caribbean", "type": "region"},
    905: {"name": "Northern America", "type": "region"},
    906: {"name": "Central Asia", "type": "region"},
    907: {"name": "Eastern Asia", "type": "region"},
    908: {"name": "Oceania", "type": "region"},
    909: {"name": "Northern Africa and Western Asia", "type": "region"},
    910: {"name": "Sub-Saharan Africa", "type": "region"},
    911: {"name": "Middle Africa", "type": "region"},
    912: {"name": "Eastern Africa", "type": "region"},
    913: {"name": "Northern Africa", "type": "region"},
    914: {"name": "Southern Africa", "type": "region"},
    915: {"name": "Caribbean", "type": "region"},
    916: {"name": "Central America", "type": "region"},
    917: {"name": "South-Eastern Asia", "type": "region"},
    918: {"name": "Southern Asia", "type": "region"},
    920: {"name": "South-Eastern Asia", "type": "region"},
    921: {"name": "Southern Asia", "type": "region"},
    922: {"name": "Western Asia", "type": "region"},
    923: {"name": "Southern Europe", "type": "region"},
    924: {"name": "Western Europe", "type": "region"},
    925: {"name": "Eastern Europe", "type": "region"},
    926: {"name": "Northern Europe", "type": "region"},
    927: {"name": "Australia and New Zealand", "type": "region"},
    928: {"name": "Melanesia", "type": "region"},
    931: {"name": "South America", "type": "region"},
    934: {"name": "Less developed regions, excl. LDC", "type": "aggregate"},
    935: {"name": "Asia", "type": "region"},
    941: {"name": "Least developed countries", "type": "aggregate"},
    943: {"name": "Lower-middle-income countries", "type": "income_group"},
    944: {"name": "Middle-income countries", "type": "income_group"},
    945: {"name": "Upper-middle-income countries", "type": "income_group"},
    946: {"name": "Low-income countries", "type": "income_group"},
    948: {"name": "High-income countries", "type": "income_group"},
    954: {"name": "Micronesia (Region)", "type": "region"},
    957: {"name": "Polynesia", "type": "region"},
    1801: {"name": "Sustainable Development Goals (SDG) regions", "type": "aggregate"},
    1802: {"name": "Sub-Saharan Africa (SDG)", "type": "region"},
    1803: {"name": "Northern Africa and Western Asia (SDG)", "type": "region"},
    1804: {"name": "Central and Southern Asia (SDG)", "type": "region"},
    1805: {"name": "Eastern and South-Eastern Asia (SDG)", "type": "region"},
    1806: {"name": "Latin America and the Caribbean (SDG)", "type": "region"},
    1807: {"name": "Oceania (SDG)", "type": "region"},
    1808: {"name": "Europe and Northern America (SDG)", "type": "region"},
}

# Known non-country aggregate entities in World Bank / UN DESA datasets
AGGREGATE_ENTITIES = {
    # World
    "WLD": {"name": "World", "type": "world"},
    "WORLD": {"name": "WORLD", "type": "world"},
    
    # World Bank Regional Aggregates
    "AFE": {"name": "Africa Eastern and Southern", "type": "region"},
    "AFW": {"name": "Africa Western and Central", "type": "region"},
    "ARB": {"name": "Arab World", "type": "region"},
    "CEB": {"name": "Central Europe and the Baltics", "type": "region"},
    "CSS": {"name": "Caribbean small states", "type": "region"},
    "EAP": {"name": "East Asia & Pacific (excluding high income)", "type": "region"},
    "EAR": {"name": "Early-demographic dividend", "type": "aggregate"},
    "EAS": {"name": "East Asia & Pacific", "type": "region"},
    "ECA": {"name": "Europe & Central Asia (excluding high income)", "type": "region"},
    "ECS": {"name": "Europe & Central Asia", "type": "region"},
    "EMU": {"name": "Euro area", "type": "aggregate"},
    "EUU": {"name": "European Union", "type": "aggregate"},
    "FCS": {"name": "Fragile and conflict affected situations", "type": "aggregate"},
    "HPC": {"name": "Heavily indebted poor countries (HIPC)", "type": "aggregate"},
    "IBD": {"name": "IBRD only", "type": "aggregate"},
    "IBT": {"name": "IDA & IBRD total", "type": "aggregate"},
    "IDA": {"name": "IDA total", "type": "aggregate"},
    "IDB": {"name": "IDA blend", "type": "aggregate"},
    "IDX": {"name": "IDA only", "type": "aggregate"},
    "LAC": {"name": "Latin America & Caribbean (excluding high income)", "type": "region"},
    "LCN": {"name": "Latin America & Caribbean", "type": "region"},
    "LDC": {"name": "Least developed countries: UN classification", "type": "aggregate"},
    "LIC": {"name": "Low income", "type": "income_group"},
    "LMC": {"name": "Lower middle income", "type": "income_group"},
    "LMY": {"name": "Low & middle income", "type": "income_group"},
    "LTE": {"name": "Late-demographic dividend", "type": "aggregate"},
    "MEA": {"name": "Middle East & North Africa", "type": "region"},
    "MIC": {"name": "Middle income", "type": "income_group"},
    "MNA": {"name": "Middle East & North Africa (excluding high income)", "type": "region"},
    "NAC": {"name": "North America", "type": "region"},
    "OED": {"name": "OECD members", "type": "aggregate"},
    "OSS": {"name": "Other small states", "type": "aggregate"},
    "PRE": {"name": "Pre-demographic dividend", "type": "aggregate"},
    "PST": {"name": "Post-demographic dividend", "type": "aggregate"},
    "SAS": {"name": "South Asia", "type": "region"},
    "SSA": {"name": "Sub-Saharan Africa", "type": "region"},
    "SSF": {"name": "Sub-Saharan Africa (excluding high income)", "type": "region"},
    "SST": {"name": "Small states", "type": "aggregate"},
    "TEA": {"name": "East Asia & Pacific (IDA & IBRD countries)", "type": "region"},
    "TEC": {"name": "Europe & Central Asia (IDA & IBRD countries)", "type": "region"},
    "TLA": {"name": "Latin America & the Caribbean (IDA & IBRD countries)", "type": "region"},
    "TMN": {"name": "Middle East & North Africa (IDA & IBRD countries)", "type": "region"},
    "TSA": {"name": "South Asia (IDA & IBRD)", "type": "region"},
    "TSS": {"name": "Sub-Saharan Africa (IDA & IBRD countries)", "type": "region"},
    "UMC": {"name": "Upper middle income", "type": "income_group"},
    "HIC": {"name": "High income", "type": "income_group"},
}

# Alias resolution mapping for various country name spellings across UN DESA and WB
COUNTRY_NAME_ALIASES = {
    "united states": "USA",
    "united states of america": "USA",
    "usa": "USA",
    "u.s.": "USA",
    "u.s.a.": "USA",
    "united kingdom": "GBR",
    "uk": "GBR",
    "great britain": "GBR",
    "russia": "RUS",
    "russian federation": "RUS",
    "south korea": "KOR",
    "korea, rep.": "KOR",
    "korea, republic of": "KOR",
    "republic of korea": "KOR",
    "north korea": "PRK",
    "korea, dem. people's rep.": "PRK",
    "democratic people's republic of korea": "PRK",
    "vietnam": "VNM",
    "viet nam": "VNM",
    "syria": "SYR",
    "syrian arab republic": "SYR",
    "iran": "IRN",
    "iran, islamic rep.": "IRN",
    "iran (islamic republic of)": "IRN",
    "venezuela": "VEN",
    "venezuela, rb": "VEN",
    "venezuela (bolivarian republic of)": "VEN",
    "bolivia": "BOL",
    "bolivia (plurinational state of)": "BOL",
    "tanzania": "TZA",
    "united republic of tanzania": "TZA",
    "laos": "LAO",
    "lao pdr": "LAO",
    "lao people's democratic republic": "LAO",
    "dr congo": "COD",
    "congo, dem. rep.": "COD",
    "democratic republic of the congo": "COD",
    "congo, rep.": "COG",
    "congo": "COG",
    "côte d'ivoire": "CIV",
    "cote d'ivoire": "CIV",
    "ivory coast": "CIV",
    "egypt, arab rep.": "EGY",
    "egypt": "EGY",
    "yemen, rep.": "YEM",
    "yemen": "YEM",
    "turkey": "TUR",
    "türkiye": "TUR",
    "czech republic": "CZE",
    "czechia": "CZE",
    "slovak republic": "SVK",
    "slovakia": "SVK",
    "moldova": "MDA",
    "republic of moldova": "MDA",
    "hong kong": "HKG",
    "hong kong sar, china": "HKG",
    "china, hong kong sar": "HKG",
    "macao": "MAC",
    "macao sar, china": "MAC",
    "china, macao sar": "MAC",
    "palestine": "PSE",
    "west bank and gaza": "PSE",
    "state of palestine": "PSE",
    "brunei": "BRN",
    "brunei darussalam": "BRN",
    "burma": "MMR",
    "myanmar": "MMR",
    "cape verde": "CPV",
    "cabo verde": "CPV",
    "eswatini": "SWZ",
    "swaziland": "SWZ",
    "east timor": "TLS",
    "timor-leste": "TLS",
    "federated states of micronesia": "FSM",
    "micronesia, fed. sts.": "FSM",
    "micronesia (fed. states of)": "FSM",
}


def build_country_reference_df() -> pd.DataFrame:
    """Build a comprehensive country reference DataFrame."""
    df = pd.DataFrame(ISO_COUNTRY_DATABASE)
    return df


def get_iso3_lookup_maps() -> Tuple[Dict[str, str], Dict[int, str], Set[str]]:
    """
    Build quick lookup dictionaries for resolving ISO-3 codes.
    
    Returns:
        Tuple[name_to_iso3, m49_to_iso3, valid_iso3_set]
    """
    name_to_iso3: Dict[str, str] = {}
    m49_to_iso3: Dict[int, str] = {}
    valid_iso3: Set[str] = set()

    for item in ISO_COUNTRY_DATABASE:
        iso3 = item["iso3"]
        name = item["name"]
        m49 = item["m49"]
        
        valid_iso3.add(iso3)
        name_clean = name.lower().replace("*", "").strip()
        name_to_iso3[name_clean] = iso3
        m49_to_iso3[int(m49)] = iso3

    # Add aliases
    for alias_name, iso3 in COUNTRY_NAME_ALIASES.items():
        name_to_iso3[alias_name.lower().strip()] = iso3

    return name_to_iso3, m49_to_iso3, valid_iso3


def resolve_country_code(
    country_name: Optional[str] = None,
    iso_code: Optional[str] = None,
    m49_code: Optional[int] = None
) -> Optional[str]:
    """
    Resolve an entity to its canonical ISO3 alpha code.
    
    Args:
        country_name: Name of country/area.
        iso_code: Existing ISO2/ISO3 code if provided.
        m49_code: UN M49 numeric code if provided.
        
    Returns:
        Optional[str]: Standardized 3-letter ISO code or None if unresolvable aggregate.
    """
    name_map, m49_map, valid_iso3 = get_iso3_lookup_maps()
    
    # 1. Direct ISO3 match
    if iso_code and isinstance(iso_code, str):
        cleaned_iso = iso_code.strip().upper()
        if cleaned_iso in valid_iso3:
            return cleaned_iso
        if cleaned_iso in AGGREGATE_ENTITIES:
            return cleaned_iso
            
    # 2. M49 Numeric match
    if m49_code is not None and not pd.isna(m49_code):
        try:
            m49_int = int(m49_code)
            if m49_int in UN_M49_AGGREGATE_CODES:
                return None  # It is an aggregate, not a sovereign/territory ISO3 code
            if m49_int in m49_map:
                return m49_map[m49_int]
        except (ValueError, TypeError):
            pass
            
    # 3. Country Name match (strip whitespace and asterisks)
    if country_name and isinstance(country_name, str):
        cleaned_name = country_name.lower().replace("*", "").strip()
        if cleaned_name in name_map:
            return name_map[cleaned_name]
            
    return None


def classify_entity_type(
    iso3_code: Optional[Any],
    country_name: Optional[str] = None,
    m49_code: Optional[int] = None
) -> str:
    """
    Classify whether a code/entity is a sovereign country, territory, region, income group, or world.
    
    Args:
        iso3_code: 3-letter ISO code.
        country_name: Optional name for extra context.
        m49_code: Optional UN M49 code.
        
    Returns:
        str: 'country', 'territory', 'region', 'income_group', 'world', or 'unknown'
    """
    if m49_code is not None and not pd.isna(m49_code):
        try:
            m49_int = int(m49_code)
            if m49_int in UN_M49_AGGREGATE_CODES:
                return UN_M49_AGGREGATE_CODES[m49_int]["type"]
        except (ValueError, TypeError):
            pass
            
    if iso3_code is None or pd.isna(iso3_code) or not isinstance(iso3_code, str):
        if country_name and isinstance(country_name, str):
            name_lower = country_name.lower().replace("*", "").strip()
            if "world" in name_lower or "total" in name_lower:
                return "world"
            if any(w in name_lower for w in ["income", "dividend", "oecd", "ida & ibrd"]):
                return "income_group"
            if any(w in name_lower for w in ["africa", "asia", "europe", "latin america", "caribbean", "oceania", "middle east", "melanesia", "polynesia", "micronesia"]):
                return "region"
        return "unknown"
    
    code = str(iso3_code).upper().strip()
    
    if code in AGGREGATE_ENTITIES:
        return AGGREGATE_ENTITIES[code]["type"]
        
    for item in ISO_COUNTRY_DATABASE:
        if item["iso3"] == code:
            return item["entity_type"]
            
    # Check if name contains known aggregate keywords
    if country_name and isinstance(country_name, str):
        name_lower = country_name.lower().replace("*", "").strip()
        if "world" in name_lower or "total" in name_lower:
            return "world"
        if any(w in name_lower for w in ["income", "dividend", "oecd", "ida & ibrd"]):
            return "income_group"
        if any(w in name_lower for w in ["africa", "asia", "europe", "latin america", "caribbean", "oceania", "middle east", "melanesia", "polynesia", "micronesia"]):
            return "region"
            
    return "unknown"
