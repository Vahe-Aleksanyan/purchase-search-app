import pandas as pd
import sqlite3
from pathlib import Path
import re
from datetime import datetime


DB = Path(__file__).parent.parent/"data"/"purchases.db"
conn = sqlite3.connect(DB)


CELL_MAP = {
    "supplier":     "F6",
    "date":         "M5",

    "product_code": "D9",
    "product_name": "G9",
    "qty":          "H9",
    "unit":         "K9",
    "price":        "L9",
    "total_price":  "O9",
}


def extract_one(path: Path) -> list[dict]:
    xl = pd.read_excel(path, header=None, engine="openpyxl")

    # Fixed header values
    supplier = xl.iat[5, 5] if xl.shape[0] > 5 else None  # F6
    date = xl.iat[4, 12] if xl.shape[0] > 4 else None     # M5

    if pd.isna(supplier) or str(supplier).strip() == "":
        supplier = "Unknown Supplier"
    if pd.isna(date):
        print(f"[SKIP] {path.name} has no valid date.")
        return []

    date_str = pd.to_datetime(date, dayfirst=True).date().isoformat()

    # Start from row 9 (0-indexed = 8)
    start_row = 8
    data_rows = []
    for i in range(start_row, xl.shape[0]):
        product_code = xl.iat[i, 3]  # D = col 4 → index 3
        if pd.isna(product_code):
            break

        row = {
            "product_code": product_code,
            "product_name": xl.iat[i, 6],   # G
            "qty":           xl.iat[i, 7],   # H
            "unit":          xl.iat[i, 10],  # K
            "price":         xl.iat[i, 11],  # L
            "total_price":   xl.iat[i, 14],  # O
            "supplier":      supplier,
            "date":          date_str,
            "source_file":   path.name
        }
        data_rows.append(row)

    if not data_rows:
        print(f"[SKIP] {path.name} has no product rows.")
    else:
        print(f"[OK] Parsed {len(data_rows)} row(s) from {path.name}")

    return data_rows

def extract_number(f):  # extract number from filename like MTIncInner123.xlsx
    match = re.search(r'(\d+)', f)
    return int(match.group(1)) if match else -1


def ingest(paths):
    all_rows = []
    for p in paths:
        rows = extract_one(p)
        all_rows.extend(rows)

    if not all_rows:
        print("No valid data found.")
        return

    df = pd.DataFrame(all_rows)
    df.drop_duplicates(subset=["product_code", "date", "supplier"], inplace=True)  # ✅ avoid IntegrityError

    df.to_sql("purchases", conn, if_exists="append", index=False)

    # Enforce IGNORE on duplicate insertion:
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA journal_mode = MEMORY;")

    conn.execute(
        "INSERT INTO purchases_fts(rowid, product_name) "
        "SELECT id, product_name FROM purchases "
        "WHERE rowid NOT IN (SELECT rowid FROM purchases_fts);"
    )
    conn.commit()

    print(f"[OK] Imported {len(df)} row(s).")



if __name__ == "__main__":
    import sys, glob
    files = sorted(
        [Path(f) for pattern in sys.argv[1:] for f in glob.glob(pattern)],
        key=lambda f: extract_number(f.name)
    )
    ingest(files)
    print(f"Imported {len(files)} file(s).")