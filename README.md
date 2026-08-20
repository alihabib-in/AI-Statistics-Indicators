# Benchmarking AI Adoption Survey 2026

An interactive Streamlit dashboard benchmarking **Abu Dhabi's individual-level AI adoption
survey** (ages 16–30) against internationally comparable, nationally representative surveys
fielded from **2023 onward** across 9 reference countries.

## Countries
Norway, Sweden, Finland, South Korea, Germany, France, Singapore, Taiwan, United Kingdom
(+ Abu Dhabi as an under-embargo "X" placeholder).

## Setup

```bash
pip install -r requirements.txt
streamlit run main.py
```

No external API keys are required. All data is loaded from local CSV files.

## Structure

```
main.py                          # Welcome page + random sample chart
app_core.py                      # Shared data-loading and chart utilities
pages/
  1_Benchmark_Explorer.py        # Question + population-segment filtered charts
  2_Survey_Sources.py            # Full source metadata with links
  3_Methodology.py               # Harmonisation and integrity notes
  4_Recommendations.py           # Evidence-driven recommendations
  5_Data_Ingestion.py            # Source directory (by country) + survey upload
data/
  benchmark_data.csv             # Long-form country/question/value records
  question_catalog.csv           # Abu Dhabi question mapping (incl. segment)
  age_band_detail.csv            # Eurostat age-band detail (16-24 / 25-34 / 16-74)
  user_contributions.csv         # User-uploaded survey data points
references/
  survey_source_catalog.csv      # Source metadata, URLs, fit/verification flags
assets/
  custom.css                     # WCAG-2.1-AA styling
```

## Features

- **ECharts visualisations** (via `streamlit-echarts`) — horizontal sorted bars with value labels,
  rich tooltips and a clean "Work Sans" typography, styled after the streamlit-echarts demo.
- **Population segment filter** (Students / Graduates / Employees / Job Seekers). Segment-specific
  benchmarks are preferred; where none exists the chart falls back to the general-population figure
  with an explicit note.
- **Data ingestion**: upload a country survey (PDF / Excel / CSV) or provide a URL, record the
  extracted figure, and it is appended to the benchmark (flagged as user-provided). The existing
  source directory is browsable and filterable by country.
- **Abu Dhabi placeholder**: shown as a grey dashed bar with no assigned value on every chart.

## Font

The app uses **Work Sans** (Google Fonts). It is applied to the Streamlit UI via `custom.css` and,
for the ECharts charts (which render in an isolated iframe), `app_core._inject_echarts_font()` patches
the installed `streamlit-echarts` `index.html` at startup to load the font, with the SVG renderer so
chart text re-renders once the font arrives. The patch is idempotent and re-applies automatically
after any `pip install`.

## Data integrity

- **Publication window:** field dates from 1 January 2023 onward.
- **Unit of analysis:** personal / individual-level AI use and sentiment only (enterprise data excluded).
- **Age band:** 16–29 is used as the closest published band to the 16–30 target; wider bands are
  labelled "adapted".
- **No fabrication:** missing country-question cells display "No equivalent data"; the Abu Dhabi
  result is shown as a grey dotted placeholder **with no value assigned** — its hover reads
  "Results under embargo — no value assigned", never a number.
- **Provenance:** every record carries a `source_id` that resolves to the source catalog, with exact
  question wording, fieldwork period, sample size and URL.

## Question coverage

All 51 benchmarkable items in the Abu Dhabi questionnaire (Parts 2–9) are catalogued in
`data/question_catalog.csv` and mapped to international comparators where one exists. Questions
without an identified comparator display a "No equivalent data" placeholder chart with Abu Dhabi
shown only as a grey dotted bar.

## Verified sources

- **Eurostat** `isoc_ai_iaiu` (2025) — use of generative AI by individuals, 16–29 (NO, SE, FI, DE, FR).
- **UK Office for National Statistics** Opinions and Lifestyle Survey (3–28 June 2026) — AI usage,
  trust and concerns, 16–29.
- **South Korea** KCC/KISDI 2024 Intelligent Information Society User Panel Survey (adapted: 15–69).
- **Taiwan** Mastercard Taiwan "2026 Survey on Consumer AI Usage Habits" (adapted: 18–65; ~70%
  weekly AI-agent use).
- **Singapore** Public First "Shaping Singapore's AI Era" (March 2026, adapted: 18+; 96% use AI at
  least monthly, 29% "Super Users").
- **Contextual:** IMDA (Singapore, work-use) and ADP Research "People at Work 2026" (global workforce).

## Updating the benchmark

Append new rows to `data/benchmark_data.csv` (and a matching entry in
`references/survey_source_catalog.csv`) to add countries, questions or survey waves.
