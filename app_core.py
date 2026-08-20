import os
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_echarts as se
from streamlit_echarts import JsCode

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
REF_DIR = BASE_DIR / "references"

ECHARTS_FONT = "'Work Sans', 'Helvetica Neue', Arial, sans-serif"

COUNTRY_ORDER = [
    "Norway", "Sweden", "Finland", "South Korea", "Germany", "France",
    "Singapore", "Taiwan", "United Kingdom", "Abu Dhabi",
]

COUNTRY_COLORS = {
    "Norway": "#2b6cb0",
    "Sweden": "#2f855a",
    "Finland": "#2c7a7b",
    "South Korea": "#6b46c1",
    "Germany": "#c05621",
    "France": "#b83280",
    "Singapore": "#2d3748",
    "Taiwan": "#3182ce",
    "United Kingdom": "#d69e2e",
    "European Union (27)": "#a0aec0",
    "Abu Dhabi": "rgba(128,128,128,0.55)",
}

ABU_DHABI = "Abu Dhabi"
EMBARGO_LABEL_EN = "TBA — Under Embargo"
EMBARGO_LABEL_AR = "قيد الإعلان — تحت الحجب"

PRIMARY_COUNTRIES = [
    "Norway", "Sweden", "Finland", "South Korea", "Germany", "France",
    "Singapore", "Taiwan", "United Kingdom",
]

ALL_COUNTRIES = PRIMARY_COUNTRIES + ["European Union (27)"]


SEGMENTS = ["All segments", "Students", "Graduates", "Employees", "Job Seekers"]


@st.cache_data(show_spinner=False)
def load_benchmark_data():
    base = pd.read_csv(DATA_DIR / "benchmark_data.csv", dtype={"value": float})
    uc_path = DATA_DIR / "user_contributions.csv"
    if uc_path.exists():
        try:
            uc = pd.read_csv(uc_path, dtype={"value": float})
            uc = uc[uc["value"].notna()] if "value" in uc.columns else uc
            if not uc.empty:
                base = pd.concat([base, uc], ignore_index=True)
        except Exception:
            pass
    return base


@st.cache_data(show_spinner=False)
def load_user_contributions():
    uc_path = DATA_DIR / "user_contributions.csv"
    if uc_path.exists():
        try:
            return pd.read_csv(uc_path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_source_catalog():
    return pd.read_csv(REF_DIR / "survey_source_catalog.csv")


@st.cache_data(show_spinner=False)
def load_question_catalog():
    return pd.read_csv(DATA_DIR / "question_catalog.csv")


@st.cache_data(show_spinner=False)
def load_age_band_detail():
    return pd.read_csv(DATA_DIR / "age_band_detail.csv")


def indicator_list(df):
    grouped = (
        df[["indicator_id", "theme", "indicator_label_en", "indicator_label_ar"]]
        .drop_duplicates()
        .sort_values(["theme", "indicator_id"])
    )
    return grouped


def indicator_rows(df, indicator_id):
    return df[df["indicator_id"] == indicator_id].copy()


def country_flag(code):
    flags = {
        "NO": "🇳🇴", "SE": "🇸🇪", "FI": "🇫🇮", "KR": "🇰🇷", "DE": "🇩🇪",
        "FR": "🇫🇷", "SG": "🇸🇬", "TW": "🇹🇼", "GB": "🇬🇧",
    }
    return flags.get(code, "🏳️")


def source_url(source_id):
    try:
        cat = load_source_catalog()
        row = cat[cat["source_id"] == source_id]
        if not row.empty:
            return str(row.iloc[0]["url"])
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# ECharts chart builders
# ---------------------------------------------------------------------------

def _inject_echarts_font():
    try:
        pkg_dir = os.path.dirname(se.__file__)
        idx = os.path.join(pkg_dir, "frontend", "build", "index.html")
        if not os.path.exists(idx):
            return
        with open(idx, "r", encoding="utf-8") as f:
            html = f.read()
        if "fonts.googleapis.com" in html:
            return
        font_link = (
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Work+Sans:'
            'wght@300;400;500;600;700;800&display=swap" rel="stylesheet">'
        )
        html = html.replace("<head>", "<head>" + font_link, 1)
        with open(idx, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass


_inject_echarts_font()


def render_echarts(options, height=400, key=None):
    se.st_echarts(options=options, height=f"{height}px", width="100%", key=key,
                  renderer="svg")


def _tooltip_formatter():
    code = (
        "function(params) {"
        "var p = params[0];"
        "if (p.data.placeholder) {"
        "return '<b>Abu Dhabi</b><br><span style=\"color:#888\">Results under embargo — no value assigned</span>';"
        "}"
        "var s = '<b>' + p.data.country + '</b><br>' + p.data.value + '%';"
        "if (p.data.ci) { s += ' <span style=\"color:#888\">(95% CI ' + p.data.ci + ')</span>'; }"
        "s += '<br><span style=\"color:#4a5568\">' + p.data.question + '</span>';"
        "s += '<br><span style=\"color:#888\">' + p.data.note + '</span>';"
        "s += '<br>Source: ' + p.data.src;"
        "return s;"
        "}"
    )
    return JsCode(code).js_code


def _base_style():
    return {
        "textStyle": {"fontFamily": ECHARTS_FONT},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "#ffffff",
            "borderColor": "#e2e8f0",
            "borderWidth": 1,
            "padding": [10, 14],
            "extraCssText": "border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.08);",
            "formatter": _tooltip_formatter(),
        },
    }


def echarts_benchmark_options(ind_df, label):
    sd = ind_df.sort_values("value", ascending=False)
    max_v = float(sd["value"].max()) if not sd.empty else 100.0

    data = []
    for _, r in sd.iterrows():
        lcl = str(r.get("lcl", "") or "").strip()
        ucl = str(r.get("ucl", "") or "").strip()
        ci = f"{lcl}–{ucl}" if lcl and ucl else ""
        data.append({
            "value": round(float(r["value"]), 1),
            "country": r["country"],
            "question": str(r.get("exact_question_wording", "") or ""),
            "note": str(r.get("note", "") or ""),
            "src": str(r.get("survey_name") or source_name(r["source_id"])),
            "ci": ci,
            "itemStyle": {"color": COUNTRY_COLORS.get(r["country"], "#4a5568")},
        })

    data.append({
        "value": round(max_v * 0.5, 1),
        "country": ABU_DHABI,
        "placeholder": True,
        "question": "",
        "note": "Data under embargo",
        "src": "Abu Dhabi AI Adoption Survey",
        "ci": "",
        "itemStyle": {
            "color": "rgba(160, 174, 192, 0.5)",
            "borderColor": "#718096",
            "borderType": "dashed",
            "borderWidth": 1.5,
        },
        "label": {"formatter": "TBA — Under Embargo", "color": "#718096", "fontStyle": "italic"},
    })

    options = {
        **_base_style(),
        "grid": {"left": 10, "right": 64, "top": 44, "bottom": 10, "containLabel": True},
        "xAxis": {
            "type": "value",
            "max": round(max_v * 1.3),
            "axisLabel": {"formatter": "{value}%", "color": "#718096"},
            "splitLine": {"lineStyle": {"color": "#edf2f7"}},
            "axisLine": {"show": False},
            "axisTick": {"show": False},
        },
        "yAxis": {
            "type": "category",
            "data": list(sd["country"]) + [ABU_DHABI],
            "inverse": True,
            "axisLabel": {"color": "#2d3748", "fontSize": 13},
            "axisLine": {"show": False},
            "axisTick": {"show": False},
        },
        "series": [{
            "name": label,
            "type": "bar",
            "data": data,
            "barMaxWidth": 32,
            "itemStyle": {"borderRadius": [0, 4, 4, 0]},
            "label": {
                "show": True, "position": "right", "color": "#4a5568",
                "formatter": "{c}%", "fontWeight": 500,
            },
        }],
    }
    return options


def echarts_zscore_options(ind_df, label):
    vals = ind_df["value"].dropna()
    mu = vals.mean()
    sd = vals.std(ddof=0)
    sd = sd if sd else 1.0
    sd_f = sd

    plot_df = ind_df.copy()
    plot_df["_z"] = (plot_df["value"] - mu) / sd_f
    plot_df = plot_df.sort_values("_z", ascending=False)
    max_abs = max([abs(v) for v in plot_df["_z"].tolist()] + [1.0])

    data = []
    for _, r in plot_df.iterrows():
        data.append({
            "value": round(float(r["_z"]), 2),
            "country": r["country"],
            "question": str(r.get("exact_question_wording", "") or ""),
            "note": str(r.get("note", "") or ""),
            "src": str(r.get("survey_name") or source_name(r["source_id"])),
            "ci": "",
            "itemStyle": {"color": COUNTRY_COLORS.get(r["country"], "#4a5568")},
        })

    data.append({
        "value": round(max_abs * 0.5, 2),
        "country": ABU_DHABI,
        "placeholder": True,
        "question": "", "note": "", "src": "", "ci": "",
        "itemStyle": {
            "color": "rgba(160, 174, 192, 0.5)",
            "borderColor": "#718096", "borderType": "dashed", "borderWidth": 1.5,
        },
        "label": {"formatter": "TBA — Under Embargo", "color": "#718096", "fontStyle": "italic"},
    })

    options = {
        **_base_style(),
        "grid": {"left": 10, "right": 64, "top": 44, "bottom": 10, "containLabel": True},
        "xAxis": {
            "type": "value",
            "min": -round(max_abs * 1.3, 2),
            "max": round(max_abs * 1.3, 2),
            "axisLabel": {"formatter": "{value}", "color": "#718096"},
            "splitLine": {"lineStyle": {"color": "#edf2f7"}},
            "axisLine": {"show": False},
            "axisTick": {"show": False},
        },
        "yAxis": {
            "type": "category",
            "data": list(plot_df["country"]) + [ABU_DHABI],
            "inverse": True,
            "axisLabel": {"color": "#2d3748", "fontSize": 13},
            "axisLine": {"show": False},
            "axisTick": {"show": False},
        },
        "series": [{
            "name": f"{label} (z-score)",
            "type": "bar",
            "data": data,
            "barMaxWidth": 32,
            "itemStyle": {"borderRadius": [0, 4, 4, 0]},
            "label": {
                "show": True, "position": "right", "color": "#4a5568",
                "formatter": JsCode(
                    "function(p){ return p.data.placeholder ? 'TBA' : (p.value>0?'+':'') + p.value; }"
                ).js_code,
            },
        }],
    }
    return options


def echarts_placeholder_options(label):
    options = {
        **_base_style(),
        "grid": {"left": 10, "right": 64, "top": 44, "bottom": 30, "containLabel": True},
        "xAxis": {"type": "value", "max": 1, "show": False},
        "yAxis": {
            "type": "category", "data": [ABU_DHABI],
            "axisLabel": {"color": "#2d3748", "fontSize": 13},
            "axisLine": {"show": False}, "axisTick": {"show": False},
        },
        "series": [{
            "name": label,
            "type": "bar",
            "data": [{
                "value": 0.5, "country": ABU_DHABI, "placeholder": True,
                "question": "", "note": "", "src": "", "ci": "",
                "itemStyle": {
                    "color": "rgba(160, 174, 192, 0.5)",
                    "borderColor": "#718096", "borderType": "dashed", "borderWidth": 1.5,
                },
                "label": {"formatter": "TBA — Under Embargo", "color": "#718096", "fontStyle": "italic", "position": "right"},
            }],
            "barMaxWidth": 32,
            "label": {"show": True, "position": "right"},
        }],
        "title": {"text": label, "left": "left", "textStyle": {"fontSize": 17, "color": "#1a365d", "fontFamily": ECHARTS_FONT}},
    }
    return options


def echarts_ageband_options(age_df):
    countries = sorted(age_df["country"].unique())
    band_colors = {"16-24": "#2b6cb0", "25-34": "#2f855a", "16-74": "#a0aec0"}
    series = []
    for band, color in band_colors.items():
        sub = age_df[age_df["age_band"] == band].set_index("country")
        vals = []
        for c in countries:
            if c in sub.index:
                vals.append(round(float(sub.loc[c, "value"]), 1))
            else:
                vals.append(None)
        series.append({
            "name": band, "type": "bar", "data": vals,
            "itemStyle": {"color": color, "borderRadius": [0, 3, 3, 0]},
            "barMaxWidth": 18,
            "label": {"show": True, "position": "right", "color": "#4a5568", "formatter": "{c}%"},
        })
    options = {
        **_base_style(),
        "legend": {"top": 0, "left": 0, "textStyle": {"fontFamily": ECHARTS_FONT, "color": "#2d3748"}},
        "grid": {"left": 10, "right": 64, "top": 40, "bottom": 10, "containLabel": True},
        "xAxis": {
            "type": "value",
            "axisLabel": {"formatter": "{value}%", "color": "#718096"},
            "splitLine": {"lineStyle": {"color": "#edf2f7"}},
            "axisLine": {"show": False}, "axisTick": {"show": False},
        },
        "yAxis": {
            "type": "category", "data": countries, "inverse": True,
            "axisLabel": {"color": "#2d3748", "fontSize": 13},
            "axisLine": {"show": False}, "axisTick": {"show": False},
        },
        "series": series,
    }
    return options


def chart_height(n_items):
    return max(420, 52 * n_items)


def source_name(source_id):
    try:
        cat = load_source_catalog()
        row = cat[cat["source_id"] == source_id]
        if not row.empty:
            return str(row.iloc[0]["institution"])
    except Exception:
        pass
    return source_id


def source_rows_for(ind_df):
    cat = load_source_catalog()
    ids = ind_df["source_id"].dropna().unique().tolist()
    known = cat[cat["source_id"].isin(ids)]
    user_ids = [i for i in ids if i not in set(cat["source_id"].tolist())]
    if not user_ids:
        return known
    synth = []
    for uid in user_ids:
        sub = ind_df[ind_df["source_id"] == uid].iloc[0]
        synth.append({
            "source_id": uid,
            "country": sub.get("country", ""),
            "country_code": sub.get("country_code", ""),
            "survey_name": sub.get("survey_name", "") or "User-uploaded survey",
            "institution": "User-provided source",
            "field_period": sub.get("age_band", ""),
            "sample_size_total": "",
            "url": sub.get("source_url", "") or "",
            "fit_level": sub.get("fit_level", "B"),
        })
    return pd.concat([known, pd.DataFrame(synth)], ignore_index=True)


def segment_records(df, indicator_id, segment):
    ind = df[df["indicator_id"] == indicator_id].copy()
    if segment in (None, "", "All segments"):
        return ind, ""
    exact = ind[ind["segment"] == segment]
    if not exact.empty:
        return exact, ""
    fb = ind[ind["segment"] == "General Population"]
    if not fb.empty:
        return fb, f"No {segment.lower()}-specific benchmark; using general-population figures."
    actual = sorted(ind["segment"].dropna().unique().tolist())
    label = ", ".join(actual) if actual else "available"
    return ind, f"No {segment.lower()}-specific benchmark available; showing {label} figures."


def kpi_cards(metrics, lang="en"):
    cards = "".join(
        f"<div style='flex:1;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;"
        f"padding:16px 18px;min-height:106px;display:flex;flex-direction:column;justify-content:center;"
        f"box-shadow:0 1px 3px rgba(26,32,44,0.06);"
        f"border-top:3px solid {m.get('accent', '#2b6cb0')};'>"
        f"<div style='color:#718096;font-size:11px;font-weight:600;letter-spacing:.05em;"
        f"text-transform:uppercase;margin-bottom:6px;'>{m['label']}</div>"
        f"<div style='color:#1a365d;font-size:24px;font-weight:700;line-height:1.15;"
        f"word-break:break-word;margin-bottom:4px;'>{m['value']}</div>"
        f"<div style='color:#a0aec0;font-size:12px;'>{m['sub']}</div></div>"
        for m in metrics
    )
    st.markdown(
        f"<div style='display:flex;gap:16px;width:100%;margin:10px 0 26px 0;'>{cards}</div>",
        unsafe_allow_html=True,
    )


def note_banner(text, kind="info", lang="en"):
    styles = {
        "info": {"bg": "#fffbeb", "border": "#f6e05e", "accent": "#d69e2e",
                 "color": "#744210", "icon": "ℹ️"},
        "warning": {"bg": "#fff5f5", "border": "#feb2b2", "accent": "#e53e3e",
                    "color": "#742a2a", "icon": "⚠️"},
    }
    s = styles.get(kind, styles["info"])
    st.markdown(
        f"<div style='display:flex;align-items:flex-start;gap:10px;background:{s['bg']};"
        f"border:1px solid {s['border']};border-left:4px solid {s['accent']};border-radius:8px;"
        f"padding:12px 16px;margin:18px 0;'>"
        f"<span style='font-size:16px;line-height:1.4;'>{s['icon']}</span>"
        f"<span style='color:{s['color']};font-size:13px;line-height:1.55;'>{text}</span></div>",
        unsafe_allow_html=True,
    )


def availability_matrix(ind_df):
    present = set(ind_df["country"].unique())
    matrix = []
    for c in PRIMARY_COUNTRIES:
        if c in present:
            r = ind_df[ind_df["country"] == c].iloc[0]
            matrix.append({
                "country": c,
                "status": "Data available" if r["fit_level"] == "A" else "Available (adapted)",
                "fit": r["fit_level"],
            })
        else:
            matrix.append({"country": c, "status": "No equivalent data", "fit": "-"})
    return pd.DataFrame(matrix)


def kpi_row(ind_df):
    vals = ind_df[ind_df["country"] != ABU_DHABI].dropna(subset=["value"])
    if vals.empty:
        return None, None, None
    leader = vals.loc[vals["value"].idxmax()]
    trailer = vals.loc[vals["value"].idxmin()]
    mean = vals["value"].mean()
    return leader, trailer, mean


T = {
    "en": {
        "app_title": "Benchmarking AI Adoption Survey 2026",
        "subtitle": "International comparison of individual AI adoption (ages 16–30), 2023 onward",
        "nav_welcome": "Welcome",
        "nav_explorer": "Benchmark Explorer",
        "nav_sources": "Survey Sources",
        "nav_methodology": "Methodology",
        "nav_recommendations": "Recommendations",
        "lang_label": "Language",
        "sample_title": "Sample comparative visual",
        "sample_blurb": "This is a demonstrative chart of one randomly selected benchmark question. Select the full question set in the Benchmark Explorer.",
        "show_sample": "Show a random sample question",
        "another": "Show another question",
        "under_embargo": "Under Embargo",
    },
    "ar": {
        "app_title": "المقارنة المرجعية لاستبيان اعتماد الذكاء الاصطناعي 2026",
        "subtitle": "مقارنة دولية لاعتماد الأفراد على الذكاء الاصطناعي (16–30 سنة)، 2023 وما بعد",
        "nav_welcome": "الرئيسية",
        "nav_explorer": "مستكشف المقارنات",
        "nav_sources": "مصادر الاستبيانات",
        "nav_methodology": "المنهجية",
        "nav_recommendations": "التوصيات",
        "lang_label": "اللغة",
        "sample_title": "مثال توضيحي للمقارنة",
        "sample_blurb": "هذا رسم توضيحي لسؤال مقارنة تم اختياره عشوائياً. اختر مجموعة الأسئلة الكاملة في مستكشف المقارنات.",
        "show_sample": "عرض سؤال عينة عشوائي",
        "another": "عرض سؤال آخر",
        "under_embargo": "قيد الحجب",
    },
}


def apply_css():
    css_path = BASE_DIR / "assets" / "custom.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                    unsafe_allow_html=True)


def lang_widget():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    with st.sidebar:
        st.session_state["lang"] = st.radio(
            T[st.session_state["lang"]]["lang_label"],
            ["en", "ar"],
            index=0 if st.session_state["lang"] == "en" else 1,
            format_func=lambda v: "English" if v == "en" else "العربية",
            horizontal=True,
        )
    return st.session_state["lang"]
