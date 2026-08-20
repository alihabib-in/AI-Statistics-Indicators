import sys
import os

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_core as ac

st.set_page_config(page_title="Benchmark Explorer", page_icon="📊", layout="wide")
ac.apply_css()
lang = ac.lang_widget()
t = ac.T[lang]

df = ac.load_benchmark_data()
qcat = ac.load_question_catalog()
age_df = ac.load_age_band_detail()

st.title(t["nav_explorer"])
st.caption(
    "Every Abu Dhabi questionnaire item is mapped to the closest international comparator "
    "(2023+ field dates, personal use, 16–30 target). Abu Dhabi is shown only as a grey dotted "
    "placeholder — no value is assigned."
)


def q_matches(row, seg):
    if seg == "All segments":
        return True
    return row["segment"] in (seg, "General Population")


with st.sidebar:
    st.subheader("Filters")
    segment = st.selectbox("Population segment", ac.SEGMENTS)

    qcat_f = qcat[qcat.apply(lambda r: q_matches(r, segment), axis=1)]
    parts = qcat_f[["part", "part_label"]].drop_duplicates().sort_values("part")

    part_label = st.selectbox("Questionnaire section", parts["part_label"].tolist())
    q_sub = qcat_f[qcat_f["part_label"] == part_label].reset_index(drop=True)
    q_opts = {f"{r['question_id']} — {r['construct']}": i for i, r in q_sub.iterrows()}
    q_choice = st.selectbox("Question", list(q_opts.keys()))
    q_row = q_sub.iloc[q_opts[q_choice]]

    selected_countries = st.multiselect(
        "Countries", ac.ALL_COUNTRIES, default=ac.ALL_COUNTRIES
    )
    view = st.radio("Scale", ["Raw percentages", "Normalised (z-score)"])
    st.markdown("---")
    st.caption("Charts carry per-country source links in the tooltip and the expandable source list below each chart.")

st.subheader(f"{q_row['question_id']} — {q_row['construct']}")
st.caption(q_row["question_en"] if lang == "en" else q_row["question_ar"])
st.caption(f"Segment: {q_row['segment']}")

raw_ids = q_row["indicator_ids"]
if pd.isna(raw_ids) or not str(raw_ids).strip():
    ind_ids = []
else:
    ind_ids = [s for s in str(raw_ids).split("|") if s.strip()]

if not ind_ids:
    ac.note_banner(
        "No equivalent international data identified for this question "
        "(research pass, August 2026). Abu Dhabi remains a grey dotted placeholder.",
        "warning",
    )
    opts = ac.echarts_placeholder_options(q_row["construct"])
    ac.render_echarts(opts, height=240, key="placeholder")
    st.stop()

for ind_id in ind_ids:
    ind_df, fb_note = ac.segment_records(df, ind_id, segment)
    if selected_countries:
        ind_df = ind_df[ind_df["country"].isin(selected_countries)]

    if ind_df.empty or ind_df["value"].dropna().empty:
        ac.note_banner("No data for the selected segment/countries on this indicator.", "info")
        continue

    label = ind_df["indicator_label_en"].iloc[0] if lang == "en" else ind_df["indicator_label_ar"].iloc[0]
    st.markdown(f"### {label}")

    leader, trailer, mean = ac.kpi_row(ind_df)
    if leader is not None:
        ac.kpi_cards([
            {"label": "Leading", "value": leader["country"],
             "sub": f"{leader['value']:.1f}%", "accent": "#2f855a"},
            {"label": "Cross-country mean", "value": f"{mean:.1f}%",
             "sub": "countries with data", "accent": "#1a365d"},
            {"label": "Trailing", "value": trailer["country"],
             "sub": f"{trailer['value']:.1f}%", "accent": "#c05621"},
        ], lang)

    if fb_note:
        ac.note_banner(fb_note, "info")

    if view == "Normalised (z-score)":
        opts = ac.echarts_zscore_options(ind_df, label)
        ac.render_echarts(opts, height=ac.chart_height(len(ind_df) + 1), key=f"{ind_id}_z")
        st.caption("Z-scores are computed only across the countries currently displayed (relative, not absolute).")
    else:
        opts = ac.echarts_benchmark_options(ind_df, label)
        ac.render_echarts(opts, height=ac.chart_height(len(ind_df) + 1), key=f"{ind_id}_raw")

    with st.expander(f"Source attribution for {label} (click to open)"):
        src = ac.source_rows_for(ind_df)
        for _, s in src.iterrows():
            flag = ac.country_flag(s["country_code"])
            fit = "adapted" if s["fit_level"] in ("B", "C") else "exact match"
            url = s.get("url", "") or ""
            link = f"[open source ↗]({url})" if url else ""
            st.markdown(
                f"- {flag} **{s['country']}** — {s['survey_name']} "
                f"({s['institution']}, fielded {s['field_period']}, n={s['sample_size_total']}) "
                f"[{fit}] {link}"
            )

    with st.expander("Data availability for this indicator"):
        st.dataframe(ac.availability_matrix(ind_df), use_container_width=True)

    csv_bytes = ind_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download this indicator (CSV)",
        csv_bytes,
        file_name=f"{ind_id}_benchmark.csv",
        mime="text/csv",
        key=f"dl_{ind_id}",
    )

    if ind_id == "USAGE_GENAI_3M":
        age_sel = age_df[age_df["country"].isin(selected_countries)] if selected_countries else age_df
        if not age_sel.empty:
            st.subheader("Age-band detail (16–24 vs 25–34 vs 16–74)")
            opts2 = ac.echarts_ageband_options(age_sel)
            ac.render_echarts(opts2, height=ac.chart_height(age_sel["country"].nunique()), key="ageband")
            st.caption(
                "Source: Eurostat isoc_ai_iaiu (2025). The 16–29 band is the closest published band to 16–30."
            )
