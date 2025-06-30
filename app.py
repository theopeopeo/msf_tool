import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import datetime
from data_loader import load_excel
from cost_model import filter_and_group_costs, summarize_annual_costs

logo = Image.open("assets/logo.png")
st.image(logo, width=200)  # Adjust width as needed

st.title("MSF Inventory Holding Cost Tool")

USERNAME = st.secrets["credentials"]["username"]
PASSWORD = st.secrets["credentials"]["password"]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state["authenticated"] = True
        else:
            st.error("Invalid credentials")
    st.stop()

st.success("Logged in successfully.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Warehouse cost overview", "Cost rate calculator", "Holding cost estimator", "Developer manual", "User manual"])

with tab1:

    # File upload
    cost_file = st.file_uploader("Upload cost excel file", type=["xlsx"])
    if cost_file:
        with st.spinner("Processing cost data..."):
            try:
                cost_df = load_excel(cost_file)
                grouped_df = filter_and_group_costs(cost_df)
                annual_summary = summarize_annual_costs(grouped_df)

                st.success("Cost file loaded and processed successfully.")
                st.subheader("Annual cost summary by project")
                st.dataframe(annual_summary)

                st.subheader("Monthly cost breakdown")
                st.write(f"{len(grouped_df)} records grouped by BudgetCode and month.")
                st.dataframe(grouped_df.head(50))
                st.download_button("Download full data", grouped_df.to_csv(index=False), file_name="monthly_costs.csv")
                
                st.subheader("Explore cost categories by project and year")

                # Dropdown selectors
                cost_df["Year"] = cost_df["DecisionMoment"].str.slice(0, 4)

                budget_options = sorted(
                    b for b in cost_df["BudgetCode"].dropna().unique()
                    if b.strip().upper() != "TOTAL"
                )
                year_options = sorted(cost_df["Year"].dropna().unique())

                selected_budget = st.selectbox("Select BudgetCode", budget_options)
                selected_year = st.selectbox("Select Year", year_options)

                # Filter by budget and year (and actuals if available)
                if "Actuals/forecast" in cost_df.columns:
                    filtered = cost_df[
                        (cost_df["BudgetCode"] == selected_budget) &
                        (cost_df["Year"] == selected_year) &
                        (cost_df["Actuals/forecast"].str.lower() == "actuals")
                    ]
                else:
                    filtered = cost_df[
                        (cost_df["BudgetCode"] == selected_budget) &
                        (cost_df["Year"] == selected_year)
                    ]

                # Group by cost category
                category_breakdown = (
                    filtered
                    .groupby("whatLVL1Desc")["Total CHF"]
                    .sum()
                    .reset_index()
                    .sort_values(by="Total CHF", ascending=False)
                    .rename(columns={"whatLVL1Desc": "Cost category"})
                )

                # Display
                st.markdown(f"**Cost breakdown for {selected_budget} in {selected_year}**")
                st.dataframe(category_breakdown.reset_index(drop=True), use_container_width=True)


                # Download button
                st.download_button(
                    label="Download category breakdown as CSV",
                    data=category_breakdown.to_csv(index=False),
                    file_name=f"{selected_budget}_{selected_year}_categories.csv",
                    mime="text/csv"
                )


                st.markdown(f"**Unique ProjectCodes:** {grouped_df['BudgetCode'].nunique()}")
                st.markdown(f"**Date Range:** {grouped_df['DecisionMoment'].min()} to {grouped_df['DecisionMoment'].max()}")
                


            except Exception as e:
                st.error(f"Failed to process file: {e}")
                
with tab2:
            st.header("Cost rate calculator")

            use_custom = st.checkbox("Calculate new rates with own cost- and inventory data", value=False)

            if not use_custom:
                st.markdown("Using **default cost coefficients** based on existing MSF data.")
                try:
                    default_path = os.path.join("data", "default_cost_coefficients.csv")
                    default_df = pd.read_csv(default_path)

                    st.dataframe(default_df)

                    st.download_button(
                        label="Download default cost coefficients",
                        data=default_df.to_csv(index=False),
                        file_name="default_cost_coefficients.csv",
                        mime="text/csv"
                    )
                except FileNotFoundError:
                    st.error("Default coefficient file not found. Please ensure it's placed in `data/`.")
            else:
                st.markdown("Upload your own data to **calculate new cost coefficients**.")
                sim_cost_file = st.file_uploader("Upload cost data", type=["xlsx"], key="sim_cost_file")
                sim_inventory_file = st.file_uploader("Upload inventory data", type=["xlsx"], key="sim_inventory_file")

                if sim_cost_file and sim_inventory_file:
                    with st.spinner("Processing your files..."):
                        try:
                            cost_df = pd.read_excel(sim_cost_file)
                            inv_df = pd.read_excel(sim_inventory_file)

                            # Cost filtering
                            cost_df["Year"] = cost_df["DecisionMoment"].astype(str).str[:4]
                            cost_df = cost_df[cost_df["Year"].isin(["2023", "2024"])]
                            if "Actuals/forecast" in cost_df.columns:
                                cost_df = cost_df[cost_df["Actuals/forecast"].str.lower() == "actuals"]
                            cost_df["Total CHF"] = pd.to_numeric(cost_df["Total CHF"], errors="coerce")

                            cost_agg = cost_df.groupby("BudgetCode")["Total CHF"].sum().reset_index()
                            cost_agg["AvgAnnualCostCHF"] = cost_agg["Total CHF"] / 2

                            # Inventory filtering
                            inv_df["actual_delivery_date"] = pd.to_datetime(inv_df["actual_delivery_date"], errors="coerce")
                            inv_df = inv_df[inv_df["actual_delivery_date"].astype(str).str.startswith(("2023", "2024"))]
                            inv_df["Year"] = inv_df["actual_delivery_date"].astype(str).str[:4]
                            inv_df["BudgetCode"] = inv_df["project_id"].astype(str).str[:-3]

                            inv_df["price_orderline"] = pd.to_numeric(inv_df["price_orderline"], errors="coerce")
                            inv_df["order_volume_m3"] = pd.to_numeric(inv_df["order_volume_m3"], errors="coerce")
                            inv_df["order_weight_kg"] = pd.to_numeric(inv_df["order_weight_kg"], errors="coerce")

                            inv_agg = inv_df.groupby("BudgetCode").agg(
                                TotalValueCHF=("price_orderline", "sum"),
                                TotalVolumeM3=("order_volume_m3", "sum"),
                                TotalWeightKG=("order_weight_kg", "sum")
                            ).reset_index()

                            merged = pd.merge(
                                cost_agg[["BudgetCode", "AvgAnnualCostCHF"]],
                                inv_agg,
                                on="BudgetCode",
                                how="inner"
                            )

                            # Compute coefficients
                            merged["CHF_per_Value"] = merged["AvgAnnualCostCHF"] / merged["TotalValueCHF"]
                            merged["CHF_per_m3"] = merged["AvgAnnualCostCHF"] / merged["TotalVolumeM3"]
                            merged["CHF_per_kg"] = merged["AvgAnnualCostCHF"] / merged["TotalWeightKG"]

                            # Drop NaNs
                            merged = merged.dropna()

                            # Apply IQR filtering
                            def iqr_filter(df, col):
                                Q1 = df[col].quantile(0.25)
                                Q3 = df[col].quantile(0.75)
                                IQR = Q3 - Q1
                                return df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]

                            for col in ["CHF_per_Value", "CHF_per_m3", "CHF_per_kg"]:
                                merged = iqr_filter(merged, col)

                            # Round for clarity
                            for col in ["AvgAnnualCostCHF", "TotalValueCHF", "TotalVolumeM3", "TotalWeightKG",
                                        "CHF_per_Value", "CHF_per_m3", "CHF_per_kg"]:
                                merged[col] = merged[col].round(2)

                            # Summary rows
                            summary = pd.DataFrame({
                                "BudgetCode": ["MEAN", "MEDIAN"],
                                "AvgAnnualCostCHF": [merged["AvgAnnualCostCHF"].mean(), merged["AvgAnnualCostCHF"].median()],
                                "TotalValueCHF": [merged["TotalValueCHF"].mean(), merged["TotalValueCHF"].median()],
                                "TotalVolumeM3": [merged["TotalVolumeM3"].mean(), merged["TotalVolumeM3"].median()],
                                "TotalWeightKG": [merged["TotalWeightKG"].mean(), merged["TotalWeightKG"].median()],
                                "CHF_per_Value": [merged["CHF_per_Value"].mean(), merged["CHF_per_Value"].median()],
                                "CHF_per_m3": [merged["CHF_per_m3"].mean(), merged["CHF_per_m3"].median()],
                                "CHF_per_kg": [merged["CHF_per_kg"].mean(), merged["CHF_per_kg"].median()],
                            }).round(2)

                            full_output = pd.concat([summary, merged], ignore_index=True)

                            st.success("New cost coefficients calculated successfully.")
                            st.dataframe(full_output)

                            # Save with timestamp
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            os.makedirs("data", exist_ok=True)
                            filename = f"custom_cost_coefficients_{timestamp}.csv"
                            filepath = os.path.join("data", filename)
                            full_output.to_csv(filepath, index=False)

                            st.download_button(
                                label="Download new cost coefficients",
                                data=full_output.to_csv(index=False),
                                file_name=filename,
                                mime="text/csv"
                            )

                        except Exception as e:
                            st.error(f"Error processing your data: {e}")
with tab3:
            st.header("Estimate Inventory Holding Costs")

            use_custom_rates = st.checkbox("Use custom cost coefficient file")

            rate_df = None
            if use_custom_rates:
                rate_file = st.file_uploader("Upload cost coefficient file", type=["csv"], key="custom_rate_upload")
                if rate_file:
                    rate_df = pd.read_csv(rate_file)
            else:
                try:
                    rate_df = pd.read_csv("data/default_cost_coefficients.csv")
                except FileNotFoundError:
                    st.error("Default cost coefficients not found. Please generate or upload one.")
            
            inv_file = st.file_uploader("Upload inventory data", type=["xlsx"], key="inv_data_upload")

            # Proceed only if we have both inventory data and cost coefficients
            if inv_file and rate_df is not None:
                with st.spinner("Processing your data..."):
                    try:
                        inventory_df = pd.read_excel(inv_file)

                        inventory_df.columns = inventory_df.columns.str.strip()
                        rate_df.columns = rate_df.columns.str.strip()

                        inventory_df["actual_delivery_date"] = pd.to_datetime(inventory_df["actual_delivery_date"], errors="coerce")
                        inventory_df["Year"] = inventory_df["actual_delivery_date"].dt.year
                        inventory_df = inventory_df[inventory_df["Year"].isin([2023, 2024])]

                        inventory_df["BudgetCode"] = inventory_df["project_id"].astype(str).str.strip()
                        inventory_df["price_orderline"] = pd.to_numeric(inventory_df["price_orderline"], errors="coerce")
                        inventory_df["order_volume_m3"] = pd.to_numeric(inventory_df["order_volume_m3"], errors="coerce")
                        inventory_df["order_weight_kg"] = pd.to_numeric(inventory_df["order_weight_kg"], errors="coerce")

                        inv_summary = (
                            inventory_df.groupby("BudgetCode")
                            .agg(
                                TotalValueCHF=("price_orderline", "sum"),
                                TotalVolumeM3=("order_volume_m3", "sum"),
                                TotalWeightKG=("order_weight_kg", "sum")
                            )
                            .reset_index()
                        )

                        # Use only the median row for cost rates
                        median_row = rate_df[rate_df["BudgetCode"].str.contains("MEDIAN", case=False, na=False)]
                        if median_row.empty:
                            st.error("Median row not found in cost rate file.")
                        else:
                            median_rates = median_row.iloc[0]

                            # Apply cost multipliers
                            inv_summary["Annual cost (value-based)"] = inv_summary["TotalValueCHF"] * median_rates["CHF_per_Value"]
                            inv_summary["Annual cost (m^3-based)"] = inv_summary["TotalVolumeM3"] * median_rates["CHF_per_m3"]
                            inv_summary["Annual cost (kg-based)"] = inv_summary["TotalWeightKG"] * median_rates["CHF_per_kg"]

                            for col in [
                                "TotalValueCHF", "TotalVolumeM3", "TotalWeightKG",
                                "Annual cost (value-based)", "Annual cost (m^3-based)", "Annual cost (kg-based)"
                            ]:
                                inv_summary[col] = inv_summary[col].round(2)

                            # Strip 'MCH' suffix from BudgetCode
                            inv_summary["BudgetCode"] = inv_summary["BudgetCode"].str.replace("MCH$", "", regex=True)

                            st.success("Inventory holding cost estimates calculated.")
                            st.dataframe(inv_summary)

                            # Dropdown to select BudgetCodes
                            selected_budgets = st.multiselect(
                                "Select BudgetCodes to filter the result",
                                options=inv_summary["BudgetCode"].unique(),
                                default=[]
                            )

                            if selected_budgets:
                                with st.spinner("Filtering selected BudgetCodes..."):
                                    filtered_df = inv_summary[inv_summary["BudgetCode"].isin(selected_budgets)]
                                    st.subheader("Filtered Inventory Holding Costs")
                                    st.dataframe(filtered_df)

                            st.download_button(
                                label="Download estimated holding costs",
                                data=inv_summary.to_csv(index=False),
                                file_name="estimated_holding_costs.csv",
                                mime="text/csv"
                            )

                    except Exception as e:
                        st.error(f"Error estimating holding costs: {e}")
            else:
                st.info("Please upload both a valid inventory file to continue.")

with tab4:
    st.header("Developer manual")
    try:
        with open("docs/dev_manual.md", "r", encoding="utf-8") as f:
            md = f.read()

        # Split by section title
        split_section = "Project structure"
        parts = md.split(split_section)

        # Show the first part with markdown
        st.markdown(parts[0] + f"## {split_section}", unsafe_allow_html=True)

        if len(parts) > 1:
            # Get only the tree block (between "Project structure" and "---")
            tree_block = parts[1].split("---")[0].strip()

            st.code(tree_block, language="text")  # Preserves formatting

            # Show the rest of the manual after '---'
            if "---" in parts[1]:
                rest = parts[1].split("---", 1)[1]
                st.markdown("---\n" + rest, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error("Developer manual not found.")

with tab5:
        st.header("User manual")
        try:
            with open("docs/user_manual.md", "r", encoding="utf-8") as f:
                md_content = f.read()
                st.markdown(md_content, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("User manual not found in docs/user_manual.md")




