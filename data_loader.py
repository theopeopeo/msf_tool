# streamlit/data_loader.py

import pandas as pd
import re

def load_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file)

    # Drop rows where BudgetCode is missing or not a valid project code
    if "BudgetCode" in df.columns:
        df = df[df["BudgetCode"].notna()]
        df["BudgetCode"] = df["BudgetCode"].astype(str).str.strip()
        
        # Remove rows where BudgetCode is 'Total' or doesn't match expected format
        df = df[~df["BudgetCode"].str.upper().eq("TOTAL")]
        df = df[df["BudgetCode"].str.match(r"^[A-Z]{2}\d{3}$")]

    return df
