

## Overview

This Streamlit-based tool helps MSF users:
- Analyze warehouse cost data (Tab 1)
- Calculate inventory cost coefficients (Tab 2)
- Estimate annual holding costs for inventory based on weight, volume, or value (Tab 3)

It’s intended for internal use and allows MSF staff to upload their own cost/inventory data or use default values.

---

Project structure

streamlit/
│
├── app.py # Main Streamlit app with tabbed UI logic
├── config.py # Constants (e.g., cost categories to include)
├── cost_coefficients.py # Cost coefficient calculation logic (used in Tab 2)
├── cost_model.py # Cost file filtering and monthly grouping (used in Tab 1)
├── data_loader.py # Excel loader/validator logic
│
├── data/
│ └── default_cost_coefficients.csv # Default cost_rates file used when custom_rates is not uploaded
│
├── docs/
│ ├── dev_manual.md # This file — developer instructions
│ └── user_manual.md # End-user manual for non-technical users



---

## Module descriptions

### 1. `app.py`
- The Streamlit frontend for the entire tool.
- Defines tabs for each major feature (cost analysis, rate calculation, cost estimation).
- Handles all user interactions: file uploads, data previews, buttons, and download logic.

### 2. `config.py`
- Defines constants like which **whatLVL1Desc** cost categories are considered valid warehouse costs.

### 3. `cost_model.py`
- Processes raw cost files:
  - Filters to **Actuals** and valid years (2023, 2024).
  - Groups by **BudgetCode** and month.
  - Prepares project-level summaries for display/download in Tab 1.

### 4. `cost_coefficients.py`
- Handles the logic to compute average annual warehouse costs per project.
- Aggregates inventory (value, weight, volume) and joins with cost data.
- Applies **IQR filtering** to eliminate outliers.
- Returns both raw and summary (mean/median) rows for use in simulations.

### 5. `data_loader.py`
- Shared utility for reading and validating Excel files into clean DataFrames.

---

## Tab logic (UI functionality)

### Tab 1 – **Warehouse cost overview**
- Upload a cost Excel file.
- Filters to "Actuals" and valid project-year rows.
- Shows breakdown by:
  - Year and project
  - Monthly totals
  - Category-level cost for selected project/year

### Tab 2 – **Cost rate calculator**
- Uses:
  - Cost file + Inventory file
- Aggregates average annual cost per project, merged with inventory volume/value/weight.
- Outliers are removed using **interquartile range (IQR)** logic.
- If user doesn’t check “Use custom data,” a default CSV from **/data** is loaded.

### Tab 3 – **Holding cost estimator**
- Inventory file is uploaded.
- Cost coefficients are either:
  - Loaded from default `data/default_cost_coefficients.csv`
  - Or uploaded manually
- Uses only the `MEDIAN` row to estimate costs for all BudgetCodes.
- Output:
  - Project-wise total value, volume, weight
  - Estimated holding cost by each dimension

---

## Data format requirements

### Cost excel file
| Column name        | Description                       |
|--------------------|------------------------------------|
| BudgetCode         | Project or mission code            |
| whatLVL1Desc       | Category of cost (e.g., storage)   |
| Total CHF          | Cost value                         |
| DecisionMoment     | Date of decision (YYYY-MM-DD)      |
| Actuals/forecast   | Should be `"Actuals"`              |

### Inventory excel file
| Column name         | Description                       |
|---------------------|------------------------------------|
| project_id          | Project or mission identifier     |
| price_orderline     | Value of each line item           |
| order_volume_m3     | Volume of each item               |
| order_weight_kg     | Weight of each item               |
| actual_delivery_date| Must include year (2023/2024)     |

---

```bash
streamlit run app.py

This tool was developed and tested in 2025 for internal MSF use.

For questions:

Contact: theo.js.malmstedt@gmail.com, ludvig.wenglen@gmail.com