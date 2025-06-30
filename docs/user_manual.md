

## Overview

This Streamlit-based tool helps MSF users:

- Analyze current and historic warehouse cost data (Tab 1)
- Calculate inventory cost coefficients (Tab 2)
- Estimate annual holding costs for inventory (Tab 3)

It is intended for internal use and assumes that users upload cost and inventory files based on MSF's data structure in provided excel files.

---

## Login

Users must authenticate with a username and password to access the app.

- Only authorized MSF users will be granted access.
- If login fails, verify your credentials or contact the system maintainer.

---

## Tab 1 - Warehouse cost overview

This tab provides a summary of warehouse-related expenses by project and year.

### Steps:

1. Upload a cost data file `.xlsx` in the MSF standard format.
2. The system filters and groups records by BudgetCode and date.
3. Output includes:
   - An annual cost summary per project
   - Monthly cost breakdowns
   - A cost category breakdown by BudgetCode and year
4. Results can be previewed or downloaded as CSV files.

---

## Tab 2 - Cost rate calculator

This section computes project-level cost coefficients used to estimate holding costs.

### Default mode:

- When no files are uploaded, the app uses precomputed cost coefficients based on MSF data from 2023–2024.
- These include average and median rates per CHF, m³, and kg.

### Custom mode:

1. Enable custom mode by checking the box.
2. Upload:
   - A cost data file `.xlsx`
   - An inventory data file `.xlsx`
3. The app:
   - Filters cost data for actuals in 2023–2024
   - Aggregates relevant inventory metrics
   - Computes holding cost coefficients per project using interquartile range (IQR) filtering to remove outliers
4. Output includes:
   - Per-project cost rates
   - Summary rows (mean and median)
   - Downloadable CSV (timestamped)

---

## Tab 3 - Estimate inventory holding costs

This tab uses the calculated rates to estimate the cost of holding inventory by project.

### Steps:

1. Choose to use:
   - The default cost coefficients (recommended), or
   - A custom coefficient file (upload .csv)
2. Upload inventory data (.xlsx)
3. The app:
   - Aggregates inventory by project (value, weight, and volume)
   - Multiplies each by the **median cost rate**
4. Output includes:
   - Estimated annual holding costs by BudgetCode
   - Filterable project selection
   - Downloadable CSV

---

## Input file requirements

### Cost file:

- Must contain columns:
  - `BudgetCode` `DecisionMoment` `Total CHF` `Actuals/forecast` `whatLVL1Desc`
- Format and headers must match the MSF-supplied template.

### Inventory file:

- Must contain columns:
  - `project_id` `actual_delivery_date` `price_orderline` `order_volume_m3` `order_weight_kg`
- The project ID will be used to derive BudgetCode.

Files that do not follow the expected format may fail to process.

---

## Recommendations

- Begin by using the default cost coefficients for consistency.
- Use the custom mode only if you are exploring alternative input scenarios.
- Archive downloaded results for traceability and reporting.

---

## Contact

For questions, contact:

 theo.js.malmstedt@gmail.com, ludvig.wenglen@gmail.com

