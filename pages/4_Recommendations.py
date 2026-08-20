import sys
import os

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_core as ac

st.set_page_config(page_title="Recommendations", page_icon="🧭", layout="wide")
ac.apply_css()
lang = ac.lang_widget()

st.title("Recommendations" if lang == "en" else "التوصيات")

df = ac.load_benchmark_data()

st.markdown(
    "Evidence-driven recommendations for Abu Dhabi stakeholders, derived strictly from the "
    "comparator-country benchmarks above. Each item cites the specific survey observation."
)

observations = {}

for ind_id in ["USAGE_GENAI_3M", "USAGE_PRIVATE", "USAGE_EDUCATION", "USAGE_WORK"]:
    sub = df[df["indicator_id"] == ind_id]
    vals = sub.dropna(subset=["value"])
    if vals.empty:
        continue
    leader = vals.loc[vals["value"].idxmax()]
    trailer = vals.loc[vals["value"].idxmin()]
    observations[ind_id] = {
        "leader": (leader["country"], leader["value"]),
        "trailer": (trailer["country"], trailer["value"]),
        "mean": vals["value"].mean(),
    }

def rec(obs, context, action, challenge, citation):
    st.markdown(f"**Observation:** {obs}")
    st.markdown(f"**Context:** {context}")
    st.markdown(f"**Actionable step:** {action}")
    st.markdown(f"**Anticipated challenge:** {challenge}")
    st.markdown(f"**Citation:** {citation}")
    st.markdown("---")


st.header("1. Global benchmark trends")

if "USAGE_GENAI_3M" in observations:
    o = observations["USAGE_GENAI_3M"]
    rec(
        f"Among 16–29 year-olds, Norway reports the highest generative-AI use in the last 3 months "
        f"({o['leader'][1]:.1f}%), Germany the lowest of the harmonised set ({o['trailer'][1]:.1f}%), "
        f"cross-country mean {o['mean']:.1f}%.",
        "Nordic countries show a high-adoption, high-trust digital environment; Germany's lower youth "
        "adoption reflects different digital-infrastructure and language contexts rather than lower capability.",
        "Position Abu Dhabi's forthcoming 16–30 usage result against this Eurostat 16–29 range "
        "(53.7%–78.3%) rather than against a single country.",
        "The Abu Dhabi question asks 'ever used', whereas Eurostat uses 'last 3 months'; use the "
        "frequency recode (Q3.03 daily/weekly/monthly) to approximate the 3-month window.",
        "Eurostat isoc_ai_iaiu (2025), dataset isoc_ai_iaiu.",
    )

st.header("2. Relationships between trust, usage and training")

rec(
    "In the United Kingdom, only 14% of 16–29 year-olds think AI has more benefits than risks, and "
    "79% worry about personal-data misuse — despite high usage (63% use AI for work or education).",
    "High usage does not imply high trust. Concern about privacy and misinformation is a separate, "
    "stronger signal among youth than usage alone would suggest.",
    "Track Abu Dhabi's Q8.01–Q8.04 (sentiment, trust, concerns) alongside Q3 usage rather than "
    "reporting usage in isolation; build a usage–trust matrix.",
    "The UK construct is not directly matched in the Eurostat set, so the trust benchmark is "
    "currently UK-anchored; broaden with Eurobarometer/Ipsos AI-trust modules as they become available.",
    "UK ONS Opinions and Lifestyle Survey (June 2026), Tables 2 & 6.",
)

st.header("3. Strategic opportunity areas")

if "USAGE_EDUCATION" in observations:
    o = observations["USAGE_EDUCATION"]
    rec(
        f"Use of generative AI for formal education is highest in Norway ({o['leader'][1]:.1f}%) and "
        f"lowest in Germany ({o['trailer'][1]:.1f}%), with France close behind Norway.",
        "Education-system integration — not just device access — is a key differentiator for youth "
        "AI uptake in Nordic and French systems.",
        "Benchmark Abu Dhabi's Q4.03/Q5.03 (homework/university use) against this education-use range; "
        "target interventions where Abu Dhabi falls below the Nordic education benchmark.",
        "Education-use measures differ across sources; ensure the Abu Dhabi denominator is restricted "
        "to students (Q1.12) to avoid diluting the rate across the full sample.",
        "Eurostat isoc_ai_iaiu (2025), 'formal education' purpose, 16–29.",
    )

st.header("4. Gaps requiring national attention")

rec(
    "Singapore reports the highest adapted AI-use figure in the set (96% use AI at least monthly; 29% "
    "are 'Super Users' — vs 12% in the US), and Taiwan reports ~70% weekly AI-agent use; both are "
    "online quota/raked panels rather than national statistical-office samples.",
    "Asia-Pacific peers show very high individual AI engagement, but the available sources use wider "
    "age bands and consumer/consultancy panels, so they are directional rather than strictly comparable "
    "to Eurostat/ONS probability samples.",
    "Treat Singapore and Taiwan as high-adoption reference points; prioritise obtaining NSO-grade "
    "probability samples (IMDA Digital Society Survey, Taiwan NDC/TWNIC) with a 16–30 band for the "
    "next build to upgrade these from adapted to exact-match comparators.",
    "Adapted items are flagged; avoid over-reading a 96% monthly-use figure against Eurostat's stricter "
    "'last 3 months' window without the caveat.",
    "Public First 'Shaping Singapore's AI Era' (March 2026); Mastercard Taiwan '2026 Survey on Consumer "
    "AI Usage Habits' (via Focus Taiwan).",
)

st.markdown("---")
st.caption(
    "Recommendations are hypotheses derived from observed cross-country patterns, not causal claims. "
    "Country size, national AI infrastructure and cultural context are considered; higher adoption is "
    "not treated as inherently superior policy."
)
