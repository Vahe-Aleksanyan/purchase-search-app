import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
import unicodedata
import tempfile

DB = Path("data/purchases.db")
st.set_page_config(page_title="Գնումների որոնում", layout="wide")

pd.set_option("display.max_colwidth", 100)

# --- Բրենդինգ ---
# st.image("assets/logo.jpg", width=120)  # Փոխարինեք ձեր լոգոյով
st.title("🛒 Գնումների փնտրում")
st.caption("Որոնեք ապրանքներ՝ ըստ անվանումի, կոդի կամ մատակարարի, և վերբեռնեք Excel փաստաթղթեր:")
st.markdown("---")

def normalize(text):
    if not text:
        return ""
    return unicodedata.normalize("NFKD", str(text)).lower().strip()


def query(sql, params=()):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def localize_columns(df):
    return df.rename(columns={
        "id": "Համար",
        "product_code": "Ապրանքի կոդ",
        "product_name": "Ապրանքի անվանում",
        "supplier": "Մատակարար",
        "date": "Ամսաթիվ",
        "qty": "Քանակ",
        "unit": "Չափման միավոր",
        "price": "Գին",
        "total_price": "Ընդհանուր գին",
        "source_file": "Աղբյուր ֆայլ"
    })


st.sidebar.header("📤 Նոր Excel փաստաթղթերի վերբեռնում")
uploads = st.sidebar.file_uploader(
    "Ընտրեք `.xlsx` ֆայլեր", type="xlsx", accept_multiple_files=True
)

if uploads:
    from ingestion.ingest_excel import ingest
    imported, failed = 0, []

    for f in uploads:
        try:
            tmp = Path(tempfile.gettempdir()) / f.name
            tmp.write_bytes(f.getbuffer())
            ingest([tmp])
            imported += 1
        except sqlite3.IntegrityError:
            failed.append((f.name, "Կրկնվող տողեր (բազայում արդեն կա)"))
        except Exception as e:
            failed.append((f.name, str(e)))

    if imported:
        st.sidebar.success(f"✅ Վերբեռնվել է {imported} ֆայլ")
    if failed:
        for fname, msg in failed:
            st.sidebar.error(f"❌ {fname} — սխալ: {msg}")


tab1, tab2, tab3 = st.tabs(["🔍 Ապրանքի կոդով", "🔍 Անվանումով", "🔍 Մատակարարով"])

with tab1:
    pid = st.text_input("Ապրանքի կոդ")
    if pid:
        df = query("SELECT * FROM purchases WHERE product_code = ?", [pid])
        st.dataframe(localize_columns(df), use_container_width=True)

with tab2:
    pname = st.text_input("Ապրանքի անվանում")
    if pname:
        pname_norm = normalize(pname)
        df = query("SELECT * FROM purchases", [])
        df["__norm__"] = df["product_name"].apply(normalize)
        filtered = df[df["__norm__"].str.contains(pname_norm)]
        st.dataframe(localize_columns(filtered.drop(columns=["__norm__"])), use_container_width=True)

with tab3:
    supp = st.text_input("Մատակարարի անուն")
    if supp:
        supp_norm = normalize(supp)
        df = query("SELECT * FROM purchases", [])
        df["__norm__"] = df["supplier"].apply(normalize)
        filtered = df[df["__norm__"].str.contains(supp_norm)]
        st.dataframe(localize_columns(filtered.drop(columns=["__norm__"])), use_container_width=True)

st.markdown("---")
st.markdown("""
    <style>
    div[data-baseweb="input"] > div {
        border: 2px solid black !important;
        border-radius: 5px;
        padding: 4px;
    }
    </style>
""", unsafe_allow_html=True)
