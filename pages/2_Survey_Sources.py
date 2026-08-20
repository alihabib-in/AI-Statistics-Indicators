import sys
import os

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_core as ac

st.set_page_config(page_title="Survey Sources", page_icon="🔗", layout="wide")
ac.apply_css()
lang = ac.lang_widget()

st.title("Survey Sources" if lang == "en" else "مصادر الاستبيانات")

st.markdown(
    """
Every benchmark value is traceable to an official, nationally representative survey fielded
**2023 onward**. Click a source to open the official report or dataset page. Full metadata is
retained for audit and reproducibility.
"""
)

cat = ac.load_source_catalog()
primary = cat[cat["country"].isin(ac.PRIMARY_COUNTRIES)]

for _, row in primary.iterrows():
    fit_badge = {"A": "Exact match", "B": "Partial (adapted)", "C": "Contextual / gap"}.get(
        row["fit_level"], row["fit_level"]
    )
    verify_badge = {
        "verified": "Verified this build",
        "compiled": "Compiled (prior research)",
        "gap": "Source identified — data pending",
    }.get(row["verification_status"], row["verification_status"])

    flag = ac.flag_img(row["country_code"])
    st.markdown(
        f"{flag}&nbsp; **{row['country']}** — {row['survey_name']}",
        unsafe_allow_html=True,
    )
    with st.expander("View details & source"):
        st.markdown(f"**Institution:** {row['institution']}")
        st.markdown(f"**Fieldwork:** {row['field_period']}  ·  **Published:** {row['publication_date']}")
        st.markdown(f"**Sample size:** {row['sample_size_total']}  ·  **Age range:** {row['age_range_covered']}")
        st.markdown(f"**Mode:** {row['survey_mode']}")
        st.markdown(f"**Methodology:** {row['methodology']}")
        st.markdown(f"**Fit level:** {fit_badge}  ·  **Verification status:** {verify_badge}")
        st.markdown(f"**License:** {row['license']}")
        st.markdown(f"**Source:** [open official source ↗]({row['url']})")
        st.markdown(f"**Notes:** {row['notes']}")

st.subheader("Secondary / contextual comparators")
st.markdown(
    "The following additional individual-level sources (non-core countries) are retained for "
    "context only and are **not** part of the 9-country personal-use benchmark."
)
secondary = pd.DataFrame([
    {
        "Country": "United States", "Code": "US",
        "Source": "Pew Research Center — About 1 in 5 US workers use AI in their job (2025)",
        "Metric": "21% of workers use AI at work",
        "Link": "https://www.pewresearch.org/short-reads/2025/10/06/about-1-in-5-us-workers-now-use-ai-in-their-job-up-since-last-year/",
    },
    {
        "Country": "Canada", "Code": "CA",
        "Source": "KPMG Generative AI Adoption Index (2025)",
        "Metric": "72% of employees use GenAI at work",
        "Link": "https://kpmg.com/ca/en/services/digital/ai-services/generative-ai-adoption-index.html",
    },
    {
        "Country": "Australia", "Code": "AU",
        "Source": "Deloitte — Generation AI (2024)",
        "Metric": "67% of students with GenAI experience",
        "Link": "https://www.deloitte.com/au/en/about/press-room/signs-australia-taking-a-shell-be-right-approach-to-gen-ai-adoption-210524.html",
    },
    {
        "Country": "Singapore", "Code": "SG",
        "Source": "IMDA — Singapore Digital Economy Report FY2024/25",
        "Metric": "73.8% of working individuals use AI at work",
        "Link": "https://www.imda.gov.sg/-/media/imda/files/about/resources/corporate-publications/annual-report/imda-sgde-report-fy2024-2025.pdf",
    },
    {
        "Country": "Global (18 markets)", "Code": "GLOBAL",
        "Source": "ADP Research — People at Work 2026",
        "Metric": "Global workforce attitudes toward AI at work (contextual)",
        "Link": "https://images.adpinfo.com/Web/ADPEmployerServices/%7B2f155459-cb30-42b0-80bd-e70d2f166af6%7D_PaW-Report-2026_EN-UK.pdf",
    },
])
for _, r in secondary.iterrows():
    flag = "🌐" if r["Code"] == "GLOBAL" else ac.flag_img(r["Code"])
    st.markdown(
        f"{flag}&nbsp; **{r['Country']}** — {r['Source']} ({r['Metric']}) [open ↗]({r['Link']})",
        unsafe_allow_html=True,
    )

st.caption("Data licensed per source. See source links and the Methodology page for harmonisation details.")
