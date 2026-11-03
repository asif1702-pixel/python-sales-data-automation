# Python Sales Data Automation

A beginner-friendly Streamlit application that cleans sales data, calculates business metrics, visualises trends, and exports a multi-sheet Excel report.

## Features

- Upload CSV or Excel (`.xlsx`, `.xls`) files
- Validate required columns and clean common formatting issues
- Remove duplicate rows
- Reject rows with invalid dates, product names, quantities, or unit prices
- Calculate revenue, units sold, record/order count, and average revenue per order
- Visualise monthly revenue and top products
- Summarise revenue by category and region when those columns are present
- Download cleaned CSV and a multi-sheet Excel report

## Required input columns

- `OrderDate`
- `Product`
- `Quantity`
- `UnitPrice`

Optional columns: `OrderID`, `Category`, `Region`, `Customer`.

Dates should ideally use `YYYY-MM-DD`. The app also attempts day-first date parsing. `Quantity` and `UnitPrice` should contain numeric values; currency symbols and commas are stripped.

## Run locally (Windows)

1. Install Python 3.10 or later from https://www.python.org/downloads/
2. Extract this project ZIP.
3. Open the project folder in VS Code.
4. Open Terminal > New Terminal.
5. Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

6. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

7. Start the app:

```powershell
streamlit run app.py
```

The app should open in your browser. If it does not, open the local URL printed in the terminal (usually http://localhost:8501).

## Test with sample data

Use `data/sample_sales.csv`, included in this repository. Upload it in the app and check:
- Total revenue is greater than zero
- Monthly revenue chart appears
- Top products chart appears
- Cleaned CSV downloads
- Excel report downloads and contains Summary, Cleaned Data, Monthly Revenue, Top Products, and Rejected Rows sheets

## Deploy free with Streamlit Community Cloud

1. Create a GitHub account.
2. Create a new **public** repository, for example `python-sales-data-automation`.
3. Upload all project files, including `app.py`, `requirements.txt`, `README.md`, and the `data` folder.
4. Visit https://share.streamlit.io/ and sign in with GitHub.
5. Select **Create app**, choose your repository, branch `main`, and main file path `app.py`.
6. Deploy. Streamlit will install packages from `requirements.txt`.
7. Test the public URL using the sample CSV.

Free hosting availability and limits can change. Do not upload confidential client sales data to a public demo. For client work, use anonymised/sample data for demonstrations and obtain permission before processing real data.

## Suggested portfolio description

**Python Sales Data Automation | Python, Pandas, Streamlit, Plotly, Excel**

Built an interactive application that cleans sales CSV/Excel files, validates records, calculates revenue KPIs, visualises monthly sales and top products, and exports cleaned datasets plus multi-sheet Excel reports.

## Important notes / limitations

- This is a portfolio demonstration, not an accounting system.
- The app assumes one row represents one product line in an order.
- If `OrderID` is present, distinct order IDs are counted. Otherwise, valid rows are counted as records.
- Average revenue per order is an estimate based on distinct order IDs (or records when no ID is supplied).
- Confirm date formats, currency, tax, refunds, discounts, and business rules with each client before using this for paid work.
- The app does not store uploaded files on purpose; files are processed in the running app session.
