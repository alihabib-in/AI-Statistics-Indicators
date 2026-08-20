import sys
import os

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_core as ac

st.set_page_config(page_title="Methodology", page_icon="📐", layout="wide")
ac.apply_css()
lang = ac.lang_widget()

st.title("Methodology Note" if lang == "en" else "المنهجية")

st.header("1. Scope and eligibility")
st.markdown(
    """
- **Target population:** general-population youth aged **16–30** (students, early-career workers,
  job seekers and those not in employment).
- **Publication window:** only surveys with field dates **from 1 January 2023 onward**.
- **Unit of analysis:** **personal/individual-level** AI use and sentiment only. Enterprise, firm-level,
  and workplace-procurement metrics are excluded.
- **Countries:** 9 primary comparators (Norway, Sweden, Finland, South Korea, Germany, France,
  Singapore, Taiwan, United Kingdom).
"""
)

st.header("2. Age-band harmonisation (16–30 target)")
st.markdown(
    """
The Abu Dhabi survey targets ages 16–30. Official sources publish standard bands rather than a
single 16–30 cut. The closest published band is used and clearly labelled:

| Source | Closest band to 16–30 | Handling |
|---|---|---|
| Eurostat (isoc_ai_iaiu) | **16–29** | Used directly as the closest published band; 16–24 and 25–34 also retained for age detail |
| UK ONS (OPN, June 2026) | **16–29** | Used directly |
| South Korea (KCC/KISDI 2024) | 15–69 | **Adapted item** — flagged, not a 16–30 band |
| Taiwan (Mastercard Taiwan 2026) | 18–65 (18–30 subgroup) | **Adapted item** — flagged |
| Singapore (Public First 2026) | 18+ | **Adapted item** — flagged |

No composite estimates are fabricated. Where only wider bands exist, the value is shown as an
**adapted item** with the original wording preserved.
"""
)

st.header("3. Construct harmonisation")
st.markdown(
    """
Every benchmarkable Abu Dhabi question (Parts 2–9) is mapped to the closest international
comparable construct. Questions with no identified comparator display **"No equivalent data"**
rather than an estimated value.

| Abu Dhabi | International equivalent | Source | Notes |
|---|---|---|---|
| Q3.01 — ever used AI | Used generative AI in last 3 months | Eurostat (NO/SE/FI/DE/FR) | Recall window differs (3 months vs ever) |
| Q3.02 — types of tools | Used for text generation (among users) | Korea KCC/KISDI | Denominator = AI users |
| Q3.03 — frequency | "Super"/daily users | Singapore, Taiwan | Adapted (age bands differ) |
| Q3.06 — paid subscription | Paid AI subscription | Korea, Taiwan | Adapted |
| Q3.08 — reasons for non-use | No need / difficult / privacy | Eurostat (EU-27), Korea | EU-27 is an aggregate reference |
| Q4.03 / Q5.03 / Q5.04 — study use | Used GenAI for formal education | Eurostat, UK | UK conflates work + education |
| Q6.04 — AI use at work | Used GenAI for professional purposes | Eurostat | Individual-reported, not enterprise |
| Q6.05 — job performance | Positive impact: make job easier | UK ONS | Proxy |
| Q6.09 / Q7.01 — AI confidence | Confident using AI tools | Singapore | Derived (100% − not-confident) |
| Q8.01 — feeling about AI | Agree AI benefits me / benefits vs risks | UK ONS | UK-only construct |
| Q8.02 — benefits | Positive impact: learning / job | UK ONS | UK-only |
| Q8.03 — concerns | Job risk / data misuse / fake content | UK ONS, Korea | UK + Korea |
| Q8.04 — trust in decisions | Trust AI for tasks / trust none | UK ONS | Proxy for decision trust |
| Q8.05 — regulation | Want government regulation/support | Korea | Adapted |
| Q9.05 — AI skills essential | AI skills essential within 5 years | Singapore | Adapted |

The UK ONS reference period is "past 12 months"; Eurostat uses "last 3 months". These are
**labelled as adapted** where they appear together.
"""
)

st.header("4. Statistical treatment")
st.markdown(
    """
- **Raw percentages** are reported with their source precision.
- **Z-score (normalised) view** standardises each question to mean 0 / SD 1 *across the displayed
  countries only*, for relative ranking — never as an absolute benchmark.
- **Confidence intervals** (95%) are shown where the source publishes them (UK ONS) and are
  displayed in tooltips.
- **Small samples** are flagged; the UK 16–29 subsample is n=280 and is noted accordingly.
"""
)

st.header("5. Abu Dhabi 'X' convention")
st.markdown(
    """
The Abu Dhabi survey results are **under embargo** and are never displayed as real values. On every
chart Abu Dhabi appears as a **grey dotted "X" placeholder** at an arbitrary height (50% of the
y-maximum), labelled **"TBA — Under Embargo"**. No value is estimated, leaked or extrapolated.
"""
)

st.header("6. Coverage and remaining gaps")
st.markdown(
    """
- **Well covered (cross-country):** AI/GenAI usage (any, private, work, education), usage by
  population segment (students, employees, unemployed), frequency/advanced use, subscriptions, and
  reasons for non-use — via Eurostat (NO/SE/FI/DE/FR + EU-27), UK ONS, Korea, Singapore, Taiwan.
- **Partly covered (1–2 countries):** trust, concerns, perceived benefits and regulation — these
  constructs have matched data for the **UK (ONS)** and **South Korea (KISDI)** only; Eurostat's
  2025 AI module does not measure attitudes.
- **Not yet benchmarked (no published cross-country individual data found):** AI knowledge
  self-rating (Q2.01), understanding of AI terms (Q2.04), following AI news (Q2.05), training
  receipt/quality (Q7.03–Q7.06), and career interest in AI/tech (Q9.01–Q9.03). These remain
  **"No equivalent data"** until a national or harmonised source is identified — they are not imputed.

Eurostat's individual AI survey currently covers only **use of generative AI** (`isoc_ai_iaiu`) and
**reasons for non-use** (`isoc_ai_iaiuxr`); there is no individual-level AI skills or knowledge
module yet.
"""
)

st.header("6b. Methodological limitations")
st.markdown(
    """
- Comparator surveys differ in mode, sampling design and reference period; comparisons are adjusted
  for methodology where possible but differences may reflect wording or cultural context, not true
  adoption gaps.
- Taiwan (Mastercard) and Singapore (Public First) are online quota/raked panels, not national
  statistical-office probability samples; treat their values as directional.
- South Korea is represented by adapted items (age 15–69); segment data from Eurostat uses a
  16–74 status breakdown rather than a 16–30 band.
"""
)

st.header("7. Reproducibility")
st.markdown(
    "Data files: `data/benchmark_data.csv`, `data/age_band_detail.csv`, "
    "`references/survey_source_catalog.csv`. Each record carries its source ID, exact question "
    "wording, fieldwork period and URL. Run `pip install -r requirements.txt` then "
    "`streamlit run main.py`."
)
