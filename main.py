import random
import sys
import os

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app_core as ac

st.set_page_config(
    page_title="Benchmarking AI Adoption Survey 2026",
    page_icon="📊",
    layout="wide",
)

ac.apply_css()
lang = ac.lang_widget()
t = ac.T[lang]

st.title(t["app_title"])
st.caption(t["subtitle"])

st.markdown(
    """
This dashboard benchmarks **Abu Dhabi's individual-level AI adoption survey** (ages 16–30)
against internationally comparable, nationally representative surveys fielded from **2023 onward**
across **9 reference countries**: Norway, Sweden, Finland, South Korea, Germany, France, Singapore,
Taiwan and the United Kingdom.

The Abu Dhabi survey results are **under embargo**. They are shown throughout as a **grey dotted
"X" placeholder** and must not be read as measured values.
"""
)

df = ac.load_benchmark_data()
indicator_df = ac.indicator_list(df)

st.header(t["sample_title"])
st.info(t["sample_blurb"])

if "sample_idx" not in st.session_state:
    st.session_state["sample_idx"] = random.randrange(len(indicator_df))

st.markdown(f"**{t['another']}**")

row = indicator_df.iloc[st.session_state["sample_idx"] % len(indicator_df)]
label = row["indicator_label_en"] if lang == "en" else row["indicator_label_ar"]
ind_df = ac.indicator_rows(df, row["indicator_id"])

opts = ac.echarts_benchmark_options(ind_df, label)
ac.render_echarts(opts, height=ac.chart_height(len(ind_df) + 1), key="sample_chart")

st.caption(
    "Demonstrative chart. Click through to the **Benchmark Explorer** to select any question, "
    "filter countries, and view full source metadata."
)

with st.expander("Sources for this sample question (click to open)"):
    src = ac.source_rows_for(ind_df)
    if src.empty:
        st.write("No sources available.")
    for _, s in src.iterrows():
        st.markdown(
            f"- **{s['country']}** — {s['survey_name']} ({s['institution']}, {s['field_year']}) "
            f"[open source ↗]({s['url']})"
        )

with st.expander("Data availability for this question"):
    st.dataframe(ac.availability_matrix(ind_df), use_container_width=True)

st.markdown("---")
st.caption(
    "Data integrity: figures are drawn from official national/European statistical sources with "
    "2023+ field dates. Cross-country comparisons are adjusted for methodological differences where "
    "possible; differences may reflect survey wording or cultural context rather than true adoption gaps."
)
