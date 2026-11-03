import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Sales Data Automation", page_icon="📊", layout="wide")

REQUIRED_COLUMNS = ["OrderDate", "Product", "Quantity", "UnitPrice"]
OPTIONAL_COLUMNS = ["OrderID", "Category", "Region", "Customer"]

st.title("📊 Sales Data Automation")
st.caption("Upload a sales CSV or Excel file, clean the data, explore performance, and export a professional report.")

with st.sidebar:
    st.header("How to use")
    st.write("1. Upload a CSV or Excel file.")
    st.write("2. Check the column mapping and data quality.")
    st.write("3. Explore sales performance.")
    st.write("4. Download the cleaned data and Excel report.")
    st.divider()
    st.caption("Expected columns: OrderDate, Product, Quantity, UnitPrice. Optional: OrderID, Category, Region, Customer.")

uploaded_file = st.file_uploader("Upload sales data", type=["csv", "xlsx", "xls"])

def read_file(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def clean_sales_data(raw):
    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    # Remove fully empty rows and duplicate rows.
    df = df.dropna(how="all").drop_duplicates()

    # Convert key fields to useful data types.
    df["OrderDate"] = pd.to_datetime(
    df["OrderDate"],
    errors="coerce",
    dayfirst=False
    )
    for col in ["Quantity", "UnitPrice"]:
        # Also handles values such as "₹1,200" and "$25.00".
        cleaned = (
            df[col].astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(r"[^0-9.\-]", "", regex=True)
        )
        df[col] = pd.to_numeric(cleaned, errors="coerce")

    df["Product"] = df["Product"].astype("string").str.strip()
    for col in OPTIONAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    # Rows with invalid dates, missing products, or invalid numeric values
    # cannot be included in a reliable sales calculation.
    valid_mask = (
        df["OrderDate"].notna()
        & df["Product"].notna()
        & (df["Product"] != "")
        & df["Quantity"].notna()
        & df["UnitPrice"].notna()
        & (df["Quantity"] > 0)
        & (df["UnitPrice"] >= 0)
    )
    rejected = df.loc[~valid_mask].copy()
    clean = df.loc[valid_mask].copy()

    clean["Revenue"] = clean["Quantity"] * clean["UnitPrice"]
    clean["YearMonth"] = clean["OrderDate"].dt.to_period("M").astype(str)
    clean = clean.sort_values("OrderDate")

    return clean, rejected, len(raw), len(df)

if uploaded_file is None:
    st.info("No file uploaded yet. You can try the included sample file: `data/sample_sales.csv`.")
    sample_path = Path(__file__).parent / "data" / "sample_sales.csv"
    if sample_path.exists():
        st.download_button(
            "Download sample sales CSV",
            data=sample_path.read_bytes(),
            file_name="sample_sales.csv",
            mime="text/csv",
        )
    st.subheader("What this tool produces")
    st.markdown("- Cleaned sales records\n- Total revenue, orders and units sold\n- Monthly revenue trend\n- Top products and category/region summaries\n- Downloadable Excel report")
    st.stop()

try:
    raw_df = read_file(uploaded_file)
    clean_df, rejected_df, original_rows, deduplicated_rows = clean_sales_data(raw_df)
except Exception as exc:
    st.error(f"Could not process this file: {exc}")
    st.stop()

if clean_df.empty:
    st.warning("No valid sales rows were found. Check the required columns and values.")
    st.stop()

st.success(f"Processed {original_rows:,} input rows. {len(clean_df):,} valid rows are ready for analysis; {len(rejected_df):,} rows were rejected.")

total_revenue = clean_df["Revenue"].sum()
total_units = clean_df["Quantity"].sum()
unique_orders = clean_df["OrderID"].nunique() if "OrderID" in clean_df.columns else len(clean_df)
average_order_value = total_revenue / unique_orders if unique_orders else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total revenue", f"₹{total_revenue:,.2f}")
c2.metric("Valid orders / records", f"{unique_orders:,}")
c3.metric("Units sold", f"{total_units:,.0f}")
c4.metric("Average revenue per order", f"₹{average_order_value:,.2f}")

st.divider()
left, right = st.columns(2)

monthly = clean_df.groupby("YearMonth", as_index=False)["Revenue"].sum()
with left:
    st.subheader("Monthly revenue")
    fig = px.line(monthly, x="YearMonth", y="Revenue", markers=True, title="Revenue by month")
    st.plotly_chart(fig, use_container_width=True)

product_sales = clean_df.groupby("Product", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False).head(10)
with right:
    st.subheader("Top 10 products")
    fig = px.bar(product_sales.sort_values("Revenue"), x="Revenue", y="Product", orientation="h", title="Products by revenue")
    st.plotly_chart(fig, use_container_width=True)

if "Category" in clean_df.columns:
    st.subheader("Revenue by category")
    category_sales = clean_df.groupby("Category", dropna=False, as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.dataframe(category_sales, use_container_width=True, hide_index=True)

if "Region" in clean_df.columns:
    st.subheader("Revenue by region")
    region_sales = clean_df.groupby("Region", dropna=False, as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.dataframe(region_sales, use_container_width=True, hide_index=True)

st.subheader("Cleaned sales data")
st.dataframe(clean_df, use_container_width=True, hide_index=True)

if not rejected_df.empty:
    with st.expander(f"Review rejected rows ({len(rejected_df):,})"):
        st.caption("These rows had missing or invalid dates, product names, quantities, or unit prices.")
        st.dataframe(rejected_df, use_container_width=True, hide_index=True)

# Build a multi-sheet Excel workbook in memory.
def build_excel_report(clean, rejected, monthly_summary, product_summary):
    output = io.BytesIO()
    summary = pd.DataFrame({
        "Metric": ["Total revenue", "Valid orders / records", "Units sold", "Average revenue per order", "Valid rows", "Rejected rows"],
        "Value": [total_revenue, unique_orders, total_units, average_order_value, len(clean), len(rejected)]
    })
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        clean.to_excel(writer, sheet_name="Cleaned Data", index=False)
        monthly_summary.to_excel(writer, sheet_name="Monthly Revenue", index=False)
        product_summary.to_excel(writer, sheet_name="Top Products", index=False)
        rejected.to_excel(writer, sheet_name="Rejected Rows", index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for column_cells in ws.columns:
                max_length = max((len(str(cell.value)) if cell.value is not None else 0) for cell in column_cells)
                ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 32)
    output.seek(0)
    return output.getvalue()

excel_bytes = build_excel_report(clean_df, rejected_df, monthly, product_sales)
csv_bytes = clean_df.to_csv(index=False).encode("utf-8")

st.divider()
st.subheader("Download your reports")
d1, d2 = st.columns(2)
with d1:
    st.download_button("Download cleaned CSV", data=csv_bytes, file_name="cleaned_sales_data.csv", mime="text/csv", use_container_width=True)
with d2:
    st.download_button("Download Excel report", data=excel_bytes, file_name="sales_analysis_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.caption(f"Report generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')}. Check the exported data before using it for business decisions.")
