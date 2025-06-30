# streamlit/config.py

# Relevant cost categories (excluding 'FREIGHT')
INCLUDED_COST_CATEGORIES = [
    "ACTIVITY & OPS SPECIFIC",
    "BASIC SUPPORT COSTS",
    "CONSTRUCTION",
    "EQUIPMENT",
    "HR WORKFORCE",
    "OTHER COSTS",
    "STAFF RELATED"
]

# Columns used in the cost model
COST_DATE_COL = "DecisionMoment"
COST_VALUE_COL = "Total CHF"
COST_CATEGORY_COL = "whatLVL1Desc"
COST_FILTER_COL = "Actuals/forecast"
COST_FILTER_VALUE = "actuals"
