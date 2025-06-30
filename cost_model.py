# streamlit/cost_model.py

import pandas as pd
from config import INCLUDED_COST_CATEGORIES, COST_CATEGORY_COL, COST_FILTER_COL, COST_FILTER_VALUE, COST_DATE_COL, COST_VALUE_COL

def filter_and_group_costs(df: pd.DataFrame) -> pd.DataFrame:
    # Always filter by cost category
    filtered = df[df[COST_CATEGORY_COL].isin(INCLUDED_COST_CATEGORIES)]

    # Conditionally filter by 'Actuals/forecast' only if the column exists
    if COST_FILTER_COL in df.columns:
        filtered = filtered[
            filtered[COST_FILTER_COL].str.lower() == COST_FILTER_VALUE
        ]

    grouped = (
        filtered
        .groupby(["BudgetCode", COST_DATE_COL])[COST_VALUE_COL]
        .sum()
        .reset_index()
    )
    return grouped
def summarize_annual_costs(grouped_df: pd.DataFrame) -> pd.DataFrame:
    df = grouped_df.copy()
    df["Year"] = df["DecisionMoment"].str.slice(0, 4)
    summary = df.groupby(["BudgetCode", "Year"])["Total CHF"].sum().reset_index()
    return summary
