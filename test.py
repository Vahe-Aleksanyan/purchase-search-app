import pandas as pd
from pathlib import Path
import string

file_path = Path("/Users/vahealeksanyan/Desktop/projects/xls‑search‑app/docs/MTIncInner1.xlsx")
xl = pd.read_excel(file_path, header=None, engine="openpyxl")

print(f"Opened: {file_path.name}")
print(f"Sheet shape: {xl.shape}\n")
print("Non-empty cells:\n" + "-" * 80)

max_col = xl.shape[1]
col_letters = list(string.ascii_uppercase) + [f"A{c}" for c in string.ascii_uppercase]  # A–Z, AA–AZ

for row_idx in range(xl.shape[0]):
    for col_idx in range(xl.shape[1]):
        value = xl.iat[row_idx, col_idx]
        if pd.notna(value) and str(value).strip() != "":
            cell = f"{col_letters[col_idx]}{row_idx + 1}"  # Excel cell name
            print(f"{cell:<5} → {repr(value)}")


