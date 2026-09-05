import json
import os

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Aspekt gold-set belgilash", page_icon="🏷️", layout="centered"
)

ASPECTS = [
    ("delivery", "Yetkazib berish"),
    ("quality", "Sifat"),
    ("price", "Narx"),
    ("seller", "Sotuvchi"),
    ("packaging", "Qadoqlash"),
    ("other", "Boshqa"),
]
POLARITY_OPTIONS = ["—", "Salbiy", "Neytral", "Ijobiy"]
POLARITY_TO_CODE = {"Salbiy": "negative", "Neytral": "neutral", "Ijobiy": "positive"}
CODE_TO_POLARITY = {v: k for k, v in POLARITY_TO_CODE.items()}

MAIN_OUT = "gold_set.jsonl"
RECHECK_OUT = "gold_set_recheck.jsonl"

st.title("🏷️ Aspekt gold-set belgilash")
st.caption(
    "300 ta sharhni qo'lda belgilash: har biri uchun qaysi aspekt(lar) bor "
    "va ularning polaritetini tanlang."
)

uploaded_file = st.file_uploader("CSV faylni yuklang (300 ta sharh)", type=["csv"])
if uploaded_file is None:
    st.info("Sharhlar joylashgan CSV faylni yuklang.")
    st.stop()

file_id = f"{uploaded_file.name}_{uploaded_file.size}"
if st.session_state.get("file_id") != file_id:
    raw_df = pd.read_csv(uploaded_file)
    st.session_state.update(
        file_id=file_id,
        raw_df=raw_df,
        text_col=None,
        id_col=None,
        df=None,
        current_idx=0,
    )

raw_df = st.session_state["raw_df"]

if st.session_state["text_col"] is None:
    st.subheader("Ustunlarni belgilang")
    st.dataframe(raw_df.head(5), use_container_width=True)
    text_col = st.selectbox("Sharh matni ustuni", options=list(raw_df.columns))
    id_col = st.selectbox(
        "ID ustuni (bo'lmasa, qator raqami ishlatiladi)",
        options=["(yo'q — qator raqami)", *list(raw_df.columns)],
    )
    if st.button("Tasdiqlash", type="primary"):
        df = raw_df.copy()
        for col in ("aspects_json", "recheck_aspects_json"):
            if col not in df.columns:
                df[col] = ""
        df["aspects_json"] = df["aspects_json"].fillna("").astype(str)
        df["recheck_aspects_json"] = df["recheck_aspects_json"].fillna("").astype(str)
        st.session_state["text_col"] = text_col
        st.session_state["id_col"] = None if id_col.startswith("(") else id_col
        st.session_state["df"] = df
        st.rerun()
    st.stop()

df = st.session_state["df"]
text_col = st.session_state["text_col"]
id_col = st.session_state["id_col"]
total = len(df)


def row_id(i):
    return str(df.loc[i, id_col]) if id_col else f"row_{i}"


def save_jsonl(col, path, limit=None):
    rows = df if limit is None else df.iloc[:limit]
    with open(path, "w", encoding="utf-8") as f:
        for i, r in rows.iterrows():
            if r[col] == "":
                continue
            aspects = json.loads(r[col])
            f.write(
                json.dumps(
                    {"id": row_id(i), "text": r[text_col], "aspects": aspects},
                    ensure_ascii=False,
                )
                + "\n"
            )


st.sidebar.header("Rejim")
recheck_mode = st.sidebar.checkbox("🔁 Qayta tekshirish rejimi (kappa uchun)")
recheck_n = st.sidebar.number_input(
    "Qayta tekshiriladigan qatorlar soni",
    min_value=1,
    max_value=total,
    value=min(50, total),
    step=1,
    disabled=not recheck_mode,
)
active_col = "recheck_aspects_json" if recheck_mode else "aspects_json"
active_limit = int(recheck_n) if recheck_mode else total

if recheck_mode:
    st.sidebar.warning(
        "Bu rejimda birinchi belgilaganingiz ko'rsatilmaydi — kelgusi kunda "
        "o'zingizga qarshi qiyoslash (Cohen's kappa) uchun."
    )
    st.session_state["current_idx"] = min(
        st.session_state["current_idx"], active_limit - 1
    )

idx = st.session_state["current_idx"]

labeled = int((df[active_col].iloc[:active_limit] != "").sum())
st.progress(labeled / active_limit if active_limit else 0)
st.write(
    f"**Belgilangan: {labeled} / {active_limit}**"
    + (" (qayta tekshirish)" if recheck_mode else "")
)

c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    if st.button("⬅️ Oldingi", use_container_width=True, disabled=idx <= 0):
        st.session_state["current_idx"] -= 1
        st.rerun()
with c3:
    if st.button(
        "Keyingi ➡️", use_container_width=True, disabled=idx >= active_limit - 1
    ):
        st.session_state["current_idx"] += 1
        st.rerun()
with c2:
    jump = st.number_input(
        "Qatorga o'tish",
        min_value=0,
        max_value=active_limit - 1,
        value=idx,
        step=1,
        label_visibility="collapsed",
    )
    if jump != idx:
        st.session_state["current_idx"] = int(jump)
        st.rerun()

idx = st.session_state["current_idx"]

st.markdown("---")
st.markdown(f"#### Sharh #{idx} — id: `{row_id(idx)}`")
st.markdown(
    f"<div style='padding:18px;border-radius:10px;background-color:#f5f5f5;"
    f"font-size:18px;color:#111;'>{df.loc[idx, text_col]}</div>",
    unsafe_allow_html=True,
)

existing_raw = df.loc[idx, active_col]
existing = (
    {a["aspect"]: a["polarity"] for a in json.loads(existing_raw)}
    if existing_raw
    else {}
)

prefill = existing if not recheck_mode else {}

st.markdown("###### Aspektlar va polaritet")
selections = {}
for key, label in ASPECTS:
    default_polarity = CODE_TO_POLARITY.get(prefill.get(key), "—")
    choice = st.radio(
        label,
        POLARITY_OPTIONS,
        horizontal=True,
        index=POLARITY_OPTIONS.index(default_polarity),
        key=f"{'rc_' if recheck_mode else ''}aspect_{key}_{idx}",
    )
    if choice != "—":
        selections[key] = POLARITY_TO_CODE[choice]

if st.button("💾 Saqlash va keyingisi", type="primary", use_container_width=True):
    aspects_list = [
        {"aspect": k, "polarity": v, "confidence": 1.0} for k, v in selections.items()
    ]
    df.loc[idx, active_col] = json.dumps(aspects_list, ensure_ascii=False)
    st.session_state["df"] = df
    save_jsonl(
        active_col,
        RECHECK_OUT if recheck_mode else MAIN_OUT,
        limit=active_limit if recheck_mode else None,
    )
    if idx < active_limit - 1:
        st.session_state["current_idx"] = idx + 1
    st.rerun()

st.markdown("---")
colA, colB = st.columns(2)
with colA:
    if os.path.exists(MAIN_OUT):
        with open(MAIN_OUT, "rb") as f:
            st.download_button(
                "⬇️ gold_set.jsonl",
                f.read(),
                "gold_set.jsonl",
                "application/json",
                use_container_width=True,
            )
with colB:
    if os.path.exists(RECHECK_OUT):
        with open(RECHECK_OUT, "rb") as f:
            st.download_button(
                "⬇️ gold_set_recheck.jsonl",
                f.read(),
                "gold_set_recheck.jsonl",
                "application/json",
                use_container_width=True,
            )

with st.expander("📊 O'z-o'ziga mosligini hisoblash (Cohen's kappa)"):
    if not (os.path.exists(MAIN_OUT) and os.path.exists(RECHECK_OUT)):
        st.caption(
            "Kappa hisoblash uchun avval asosiy va qayta-tekshirish belgilashlarini tugating."
        )
    else:
        from sklearn.metrics import cohen_kappa_score

        with open(MAIN_OUT, encoding="utf-8") as f:
            main_lines = f.readlines()
        with open(RECHECK_OUT, encoding="utf-8") as f:
            recheck_lines = f.readlines()

        main_rows = {
            json.loads(line)["id"]: json.loads(line)["aspects"] for line in main_lines
        }
        recheck_rows = {
            json.loads(line)["id"]: json.loads(line)["aspects"]
            for line in recheck_lines
        }
        common_ids = [i for i in recheck_rows if i in main_rows]
        if len(common_ids) < 2:
            st.caption("Kappa hisoblash uchun umumiy qatorlar yetarli emas.")
        else:
            results = []
            for key, label in ASPECTS:
                y1 = [
                    1 if key in {a["aspect"] for a in main_rows[i]} else 0
                    for i in common_ids
                ]
                y2 = [
                    1 if key in {a["aspect"] for a in recheck_rows[i]} else 0
                    for i in common_ids
                ]
                if len(set(y1)) < 2 and len(set(y2)) < 2:
                    kappa = float("nan")
                else:
                    kappa = cohen_kappa_score(y1, y2)
                results.append(
                    {
                        "Aspekt": label,
                        "Kappa (mavjudlik)": round(kappa, 3),
                        "N": len(common_ids),
                    }
                )
            st.dataframe(
                pd.DataFrame(results), use_container_width=True, hide_index=True
            )
            st.caption(
                "Kappa < 0.6 bo'lsa, taksonomiya noaniq — ta'riflarni aniqlashtirish kerak."
            )