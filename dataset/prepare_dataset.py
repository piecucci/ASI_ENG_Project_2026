"""
Instructor-only script: Prepare the Iowa Liquor Sales dataset for the ASI course.

This script queries the Iowa Liquor Sales public dataset from data.iowa.gov
using the Socrata Open Data API (SODA), aggregates transactions to
store-category-month level, filters to the top 50 stores by total sales,
and produces train/drift-test/holdout CSV splits.

Prerequisites:
    pip install sodapy pandas   # or: uv add sodapy pandas

Usage:
    python prepare_dataset.py

No API key is required -- data.iowa.gov serves this dataset publicly.
An app token is optional but avoids throttling for large queries.
Set the environment variable SOCRATA_APP_TOKEN if you have one.
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd

try:
    from sodapy import Socrata
except ImportError:
    print(
        "ERROR: sodapy is not installed.\n"
        "Install it with:  pip install sodapy   (or:  uv add sodapy)\n"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DOMAIN = "data.iowa.gov"
DATASET_ID = "m3tr-qhgy"
APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN", None)

YEAR_MIN = 2017
YEAR_MAX = 2023
TOP_N_STORES = 50

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FULL = OUTPUT_DIR / "iowa_liquor_sales_aggregated.csv"
OUTPUT_TRAIN = OUTPUT_DIR / "iowa_liquor_train.csv"
OUTPUT_DRIFT = OUTPUT_DIR / "iowa_liquor_drift_test.csv"
OUTPUT_HOLDOUT = OUTPUT_DIR / "iowa_liquor_holdout.csv"

# The SODA API has a per-request row limit.  We page through in chunks.
PAGE_SIZE = 50_000

# ---------------------------------------------------------------------------
# BigQuery fallback SQL (printed if the SODA API is unreachable)
# ---------------------------------------------------------------------------
BIGQUERY_SQL = f"""
-- Google BigQuery fallback (dataset: bigquery-public-data.iowa_liquor_sales.sales)
SELECT
    store_number,
    store_name,
    city,
    county,
    category_name,
    EXTRACT(YEAR  FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    COUNT(*)                  AS num_transactions,
    SUM(bottles_sold)         AS total_bottles,
    SUM(sale_dollars)         AS total_sales,
    SUM(volume_sold_liters)   AS total_volume_liters,
    AVG(state_bottle_retail)  AS avg_bottle_price
FROM `bigquery-public-data.iowa_liquor_sales.sales`
WHERE EXTRACT(YEAR FROM date) BETWEEN {YEAR_MIN} AND {YEAR_MAX}
GROUP BY store_number, store_name, city, county, category_name, year, month
ORDER BY store_number, year, month;
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_all_records(client: Socrata, dataset_id: str) -> pd.DataFrame:
    """Page through the SODA API and return all matching rows as a DataFrame."""
    all_records: list[dict] = []
    offset = 0

    soql_select = (
        "store_number, store_name, city, county, category_name, "
        "date_trunc_ym(date) AS year_month, "
        "count(*) AS num_transactions, "
        "sum(bottles_sold) AS total_bottles, "
        "sum(sale_dollars) AS total_sales, "
        "sum(volume_sold_liters) AS total_volume_liters, "
        "avg(state_bottle_retail) AS avg_bottle_price"
    )
    soql_where = f"date >= '{YEAR_MIN}-01-01' AND date < '{YEAR_MAX + 1}-01-01'"
    soql_group = "store_number, store_name, city, county, category_name, date_trunc_ym(date)"

    print(f"Fetching data from {DOMAIN} (dataset {dataset_id}) ...")
    while True:
        print(f"  offset={offset} ...", end=" ", flush=True)
        t0 = time.time()
        page = client.get(
            dataset_id,
            select=soql_select,
            where=soql_where,
            group=soql_group,
            limit=PAGE_SIZE,
            offset=offset,
            order="store_number, year_month",
        )
        elapsed = time.time() - t0
        print(f"got {len(page)} rows in {elapsed:.1f}s")

        if not page:
            break
        all_records.extend(page)
        offset += PAGE_SIZE

    if not all_records:
        raise RuntimeError(
            "SODA API returned zero rows.  The service may be temporarily unavailable.\n"
            "As a fallback you can run the following SQL in Google BigQuery:\n"
            + BIGQUERY_SQL
        )

    return pd.DataFrame.from_records(all_records)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to proper types and extract year/month."""
    numeric_cols = [
        "store_number",
        "num_transactions",
        "total_bottles",
        "total_sales",
        "total_volume_liters",
        "avg_bottle_price",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # year_month comes back as e.g. "2019-03-01T00:00:00.000"
    df["year_month_dt"] = pd.to_datetime(df["year_month"], errors="coerce")
    df["year"] = df["year_month_dt"].dt.year.astype(int)
    df["month"] = df["year_month_dt"].dt.month.astype(int)
    df.drop(columns=["year_month", "year_month_dt"], inplace=True)

    # Drop rows where critical columns are null
    df.dropna(subset=["store_number", "total_sales", "year", "month"], inplace=True)

    # Ensure string columns are clean
    for col in ["store_name", "city", "county", "category_name"]:
        df[col] = df[col].fillna("UNKNOWN").astype(str).str.strip()

    return df


def filter_top_stores(df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """Keep only the top_n stores ranked by total_sales across all years."""
    store_totals = df.groupby("store_number")["total_sales"].sum()
    top_stores = store_totals.nlargest(top_n).index
    filtered = df[df["store_number"].isin(top_stores)].copy()
    print(f"Filtered to top {top_n} stores: {len(filtered)} rows (from {len(df)})")
    return filtered


def split_and_save(df: pd.DataFrame) -> None:
    """Split into train / drift-test / holdout and write CSVs."""
    # Canonical column order
    col_order = [
        "store_number",
        "store_name",
        "city",
        "county",
        "category_name",
        "year",
        "month",
        "num_transactions",
        "total_bottles",
        "total_sales",
        "total_volume_liters",
        "avg_bottle_price",
    ]
    df = df[col_order].sort_values(["store_number", "year", "month"]).reset_index(drop=True)

    # Full file
    df.to_csv(OUTPUT_FULL, index=False)
    print(f"Saved full dataset: {OUTPUT_FULL}  ({len(df)} rows)")

    # Train: 2017-2019
    train = df[df["year"].between(2017, 2019)].reset_index(drop=True)
    train.to_csv(OUTPUT_TRAIN, index=False)
    print(f"Saved train set:    {OUTPUT_TRAIN}  ({len(train)} rows)")

    # Drift test: 2020-2021 (add year_month for monthly evaluation)
    drift = df[df["year"].between(2020, 2021)].copy().reset_index(drop=True)
    drift["year_month"] = drift["year"].astype(str) + "-" + drift["month"].astype(str).str.zfill(2)
    drift.to_csv(OUTPUT_DRIFT, index=False)
    print(f"Saved drift test:   {OUTPUT_DRIFT}  ({len(drift)} rows)")

    # Holdout: 2022-2023
    holdout = df[df["year"].between(2022, 2023)].reset_index(drop=True)
    holdout.to_csv(OUTPUT_HOLDOUT, index=False)
    print(f"Saved holdout set:  {OUTPUT_HOLDOUT}  ({len(holdout)} rows)")


def print_summary(df: pd.DataFrame) -> None:
    """Print summary statistics for the full aggregated dataset."""
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)
    print(f"Rows:    {len(df)}")
    print(f"Columns: {df.shape[1]}")
    print(f"Years:   {sorted(df['year'].unique())}")
    print(f"Stores:  {df['store_number'].nunique()}")
    print(f"Categories: {df['category_name'].nunique()}")
    print(f"\nTarget (total_sales) distribution:")
    print(df["total_sales"].describe().to_string())
    print("=" * 60)

    # Split counts
    train_rows = len(df[df["year"].between(2017, 2019)])
    drift_rows = len(df[df["year"].between(2020, 2021)])
    holdout_rows = len(df[df["year"].between(2022, 2023)])
    print(f"\nSplit sizes:")
    print(f"  Train (2017-2019):      {train_rows}")
    print(f"  Drift test (2020-2021): {drift_rows}")
    print(f"  Holdout (2022-2023):    {holdout_rows}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        client = Socrata(DOMAIN, APP_TOKEN, timeout=60)
        raw_df = fetch_all_records(client, DATASET_ID)
    except Exception as exc:
        print(f"\nERROR: Failed to fetch data from SODA API.\n  {exc}\n")
        print("FALLBACK: You can run the equivalent query in Google BigQuery:")
        print(BIGQUERY_SQL)
        print(
            "Alternatively, run  generate_synthetic.py  to create a synthetic "
            "dataset with the same schema for local testing."
        )
        sys.exit(1)

    df = clean_dataframe(raw_df)
    df = filter_top_stores(df, TOP_N_STORES)
    print_summary(df)
    split_and_save(df)

    print("Done. Dataset files are in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
