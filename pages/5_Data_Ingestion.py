import sys
import os
import io
import csv
import datetime

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_core as ac

st.set_page_config(page_title="Data Ingestion", page_icon="📥", layout="wide")
ac.apply_css()
lang = ac.lang_widget()

DATA_DIR = ac.DATA_DIR
UC_PATH = DATA_DIR / "user_contributions.csv"

COUNTRY_CODE = {
    "Norway": "NO", "Sweden": "SE", "Finland": "FI", "South Korea": "KR",
    "Germany": "DE", "France": "FR", "Singapore": "SG", "Taiwan": "TW",
    "United Kingdom": "GB", "European Union (27)": "EU27",
}

BM_COLUMNS = [
    "country", "country_code", "indicator_id", "theme", "indicator_label_en",
    "indicator_label_ar", "value", "age_band", "unit", "lcl", "ucl", "source_id",
    "exact_question_wording", "note", "fit_level", "is_adapted", "segment",
    "survey_name", "source_url",
]

st.title("Data Ingestion")


def extract_preview(f):
    name = f.name.lower()
    try:
        if name.endswith(".pdf"):
            import pdfplumber
            with pdfplumber.open(io.BytesIO(f.getvalue())) as pdf:
                return "\n".join((p.extract_text() or "") for p in pdf.pages[:5])
        if name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(f.getvalue()), nrows=20)
            return df.to_string(max_colwidth=40)
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(f.getvalue()), nrows=20)
            return df.to_string(max_colwidth=40)
    except Exception as e:
        return f"[preview failed: {e}]"
    return ""


# ---------------------------------------------------------------------------
# 1) Upload / add a survey data point
# ---------------------------------------------------------------------------
st.header("Add / upload a country survey")
st.caption(
    "Upload a survey file (PDF/Excel/CSV) or provide a URL, then record the extracted "
    "figure. Contributions are appended to the benchmark (flagged as user-provided)."
)

uploaded = st.file_uploader("Upload survey file (PDF / Excel / CSV) — optional", type=["pdf", "xlsx", "xls", "csv"])
preview_text = ""
if uploaded is not None:
    preview_text = extract_preview(uploaded)
    with st.expander("File preview (extracted text — read to extract the figure)"):
        st.text(preview_text[:4000] if preview_text else "(no text extracted)")

df_all = ac.load_benchmark_data()
ind_list = df_all[["indicator_id", "indicator_label_en", "theme"]].drop_duplicates().sort_values("theme")

with st.form("add_point", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        country_choice = st.selectbox("Country", list(COUNTRY_CODE.keys()))
        segment = st.selectbox("Population segment", ["General Population", "Students", "Graduates", "Employees", "Job Seekers"])
        value = st.number_input("Value (%)", min_value=0.0, max_value=100.0, step=0.1)
    with c2:
        age_band = st.text_input("Age band", value="16-30")
        indicator_choice = st.selectbox(
            "Map to indicator",
            ["(new indicator)"] + ind_list["indicator_id"].tolist(),
            format_func=lambda x: x if x == "(new indicator)" else f"{x} — {ind_list[ind_list['indicator_id'] == x]['indicator_label_en'].iloc[0]}",
        )
        source_url = st.text_input("Source URL")

    survey_name = st.text_input("Survey name / title")
    institution = st.text_input("Institution")
    question_wording = st.text_input("Exact question wording")
    notes = st.text_area("Notes / methodology / caveats")

    submitted = st.form_submit_button("Add data point")

if submitted:
    if survey_name.strip() == "":
        st.error("Please provide a survey name.")
    elif value == 0.0:
        st.error("Please provide a value greater than 0.")
    else:
        src_id = "USER_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if indicator_choice == "(new indicator)":
            ind_id = "USER_" + src_id
            theme = "User contribution"
            label_en = survey_name.strip()
            label_ar = survey_name.strip()
        else:
            ind_id = indicator_choice
            base = ind_list[ind_list["indicator_id"] == indicator_choice].iloc[0]
            theme = base["theme"]
            label_en = base["indicator_label_en"]
            label_ar = base["indicator_label_ar"]

        note_final = notes.strip()
        if preview_text:
            note_final = (note_final + " | File preview: " + preview_text[:500]).strip()

        record = {
            "country": country_choice,
            "country_code": COUNTRY_CODE[country_choice],
            "indicator_id": ind_id,
            "theme": theme,
            "indicator_label_en": label_en,
            "indicator_label_ar": label_ar,
            "value": value,
            "age_band": age_band,
            "unit": "%",
            "lcl": "",
            "ucl": "",
            "source_id": src_id,
            "exact_question_wording": question_wording,
            "note": note_final,
            "fit_level": "B",
            "is_adapted": "1",
            "segment": segment,
            "survey_name": survey_name,
            "source_url": source_url,
        }
        with open(UC_PATH, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=BM_COLUMNS)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(record)

        ac.load_benchmark_data.clear()
        ac.load_user_contributions.clear()
        st.success(f"Added data point for {country_choice} ({value:.1f}%).")

st.divider()

# ---------------------------------------------------------------------------
# 3) Existing contributions
# ---------------------------------------------------------------------------
st.header("Uploaded contributions")
uc = ac.load_user_contributions()
if uc.empty:
    st.info("No user contributions yet.")
else:
    st.dataframe(uc[["country", "segment", "indicator_id", "value", "age_band", "survey_name", "source_url"]],
                 use_container_width=True)
    if st.button("Clear all uploaded contributions"):
        with open(UC_PATH, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=BM_COLUMNS)
            w.writeheader()
        ac.load_benchmark_data.clear()
        ac.load_user_contributions.clear()
        st.success("Cleared all uploaded contributions.")
