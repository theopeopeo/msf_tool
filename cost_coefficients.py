import pandas as pd
from config import INCLUDED_COST_CATEGORIES

def compute_cost_coefficients(cost_df: pd.DataFrame, inventory_df: pd.DataFrame) -> pd.DataFrame:
    # Clean and normalize columns
    cost_df.columns = cost_df.columns.str.strip()
    inventory_df.columns = inventory_df.columns.str.strip()

    cost_df["Year"] = pd.to_datetime(cost_df["DecisionMoment"], errors='coerce').dt.year
    inventory_df["Year"] = pd.to_datetime(inventory_df["actual_delivery_date"], errors='coerce').dt.year

    # Filter to 2023 and 2024
    cost_df = cost_df[cost_df["Year"].isin([2023, 2024])]
    inventory_df = inventory_df[inventory_df["Year"].isin([2023, 2024])]

    # Clean BudgetCode/project_id
    cost_df["BudgetCode"] = cost_df["BudgetCode"].str.strip()
    inventory_df["project_id"] = inventory_df["project_id"].str.strip()

    # Apply cost filter if column exists
    if "Actuals/forecast" in cost_df.columns:
        cost_df = cost_df[cost_df["Actuals/forecast"].str.lower() == "actuals"]

    # Include only allowed cost categories
    cost_df = cost_df[cost_df["whatLVL1Desc"].isin(INCLUDED_COST_CATEGORIES)]

    # Aggregate cost
    cost_summary = (
        cost_df.groupby("BudgetCode")["Total CHF"]
        .sum()
        .div(2)
        .reset_index()
        .rename(columns={"Total CHF": "AvgAnnualCostCHF"})
    )

    # Aggregate inventory
    inv_summary = (
        inventory_df.groupby("project_id")[["invoiced_amount", "order_volume_m3", "order_weight_kg"]]
        .sum()
        .reset_index()
        .rename(columns={
            "project_id": "BudgetCode",
            "invoiced_amount": "TotalValueCHF",
            "order_volume_m3": "TotalVolumeM3",
            "order_weight_kg": "TotalWeightKG"
        })
    )

    # Merge and compute coefficients
    merged = pd.merge(cost_summary, inv_summary, on="BudgetCode")
    merged["CHF_per_Value"] = merged["AvgAnnualCostCHF"] / merged["TotalValueCHF"]
    merged["CHF_per_m3"] = merged["AvgAnnualCostCHF"] / merged["TotalVolumeM3"]
    merged["CHF_per_kg"] = merged["AvgAnnualCostCHF"] / merged["TotalWeightKG"]

    return merged
