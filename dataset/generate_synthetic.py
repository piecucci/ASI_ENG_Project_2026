"""
Fallback script: Generate a synthetic Iowa Liquor Sales dataset.

Use this when the SODA API is unavailable or when students want to test
locally without downloading real data. The generated data mimics the
real Iowa Liquor Sales structure with:
  - ~30,000 rows at store-category-month granularity
  - Log-normal sales distributions
  - Seasonal patterns (higher sales in summer/holidays)
  - Realistic COVID-era drift in 2020-2021 (mean sales +15%, category mix shift)

Prerequisites:
    pip install numpy pandas   # or: uv add numpy pandas

Usage:
    python generate_synthetic.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
YEAR_MIN = 2017
YEAR_MAX = 2023
NUM_STORES = 50
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FULL = OUTPUT_DIR / "iowa_liquor_sales_aggregated.csv"
OUTPUT_TRAIN = OUTPUT_DIR / "iowa_liquor_train.csv"
OUTPUT_DRIFT = OUTPUT_DIR / "iowa_liquor_drift_test.csv"
OUTPUT_HOLDOUT = OUTPUT_DIR / "iowa_liquor_holdout.csv"

# ---------------------------------------------------------------------------
# Reference data: realistic Iowa store / city / county / category names
# ---------------------------------------------------------------------------
STORE_TEMPLATES = [
    ("Hy-Vee #{i}", "Des Moines", "Polk"),
    ("Hy-Vee #{i}", "Cedar Rapids", "Linn"),
    ("Hy-Vee #{i}", "Davenport", "Scott"),
    ("Hy-Vee #{i}", "Waterloo", "Black Hawk"),
    ("Hy-Vee #{i}", "Iowa City", "Johnson"),
    ("Fareway #{i}", "Ames", "Story"),
    ("Fareway #{i}", "Sioux City", "Woodbury"),
    ("Fareway #{i}", "Council Bluffs", "Pottawattamie"),
    ("Sam's Club #{i}", "West Des Moines", "Polk"),
    ("Costco #{i}", "Coralville", "Johnson"),
    ("Walmart #{i}", "Ankeny", "Polk"),
    ("Walmart #{i}", "Marion", "Linn"),
    ("Casey's #{i}", "Urbandale", "Polk"),
    ("Casey's #{i}", "Bettendorf", "Scott"),
    ("Kum & Go #{i}", "Clive", "Polk"),
    ("Kum & Go #{i}", "Johnston", "Polk"),
    ("Central City Liquor #{i}", "Des Moines", "Polk"),
    ("Smokin' Joe's #{i}", "Cedar Rapids", "Linn"),
    ("Liquor Barn #{i}", "Dubuque", "Dubuque"),
    ("Target #{i}", "West Des Moines", "Polk"),
]

CATEGORIES = [
    "VODKA 80 PROOF",
    "CANADIAN WHISKIES",
    "WHISKEY LIQUEUR",
    "SPICED RUM",
    "STRAIGHT BOURBON WHISKIES",
    "BLENDED WHISKIES",
    "TEQUILA",
    "IMPORTED VODKA",
    "AMERICAN DRY GINS",
    "TENNESSEE WHISKIES",
    "CREAM LIQUEURS",
    "SCOTCH WHISKIES",
    "SINGLE MALT SCOTCH",
    "IMPORTED SCHNAPPS",
    "AMERICAN BRANDIES",
    "FLAVORED RUM",
    "COFFEE LIQUEURS",
    "GOLD RUM",
    "WHITE RUM",
    "TRIPLE SEC",
]

# Relative popularity weights for categories (sums roughly to 1)
CATEGORY_WEIGHTS = np.array([
    0.16, 0.12, 0.10, 0.08, 0.08,
    0.06, 0.06, 0.05, 0.04, 0.04,
    0.03, 0.03, 0.02, 0.02, 0.02,
    0.02, 0.02, 0.02, 0.02, 0.01,
])
CATEGORY_WEIGHTS = CATEGORY_WEIGHTS / CATEGORY_WEIGHTS.sum()

# Seasonal multipliers by month (1-indexed, so index 0 is unused)
SEASONALITY = np.array([
    0.0,   # placeholder for month 0
    0.85,  # Jan
    0.80,  # Feb
    0.90,  # Mar
    0.95,  # Apr
    1.05,  # May
    1.10,  # Jun
    1.15,  # Jul
    1.05,  # Aug
    0.95,  # Sep
    1.05,  # Oct
    1.10,  # Nov
    1.30,  # Dec (holidays)
])

# COVID-era drift parameters (2020-2021)
COVID_SALES_MULTIPLIER = 1.15       # mean sales up ~15%
COVID_VARIANCE_BOOST = 1.20         # more variance
COVID_CATEGORY_SHIFT = {
    "VODKA 80 PROOF": 1.25,         # vodka surges
    "WHISKEY LIQUEUR": 1.20,
    "CREAM LIQUEURS": 1.30,
    "IMPORTED VODKA": 1.20,
    "TEQUILA": 0.85,                # tequila dips
    "SCOTCH WHISKIES": 0.80,
    "SINGLE MALT SCOTCH": 0.75,
}


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def build_stores(rng: np.random.Generator, n: int) -> pd.DataFrame:
    """Create a table of n synthetic stores."""
    stores = []
    for i in range(n):
        template = STORE_TEMPLATES[i % len(STORE_TEMPLATES)]
        store_number = 2000 + i * 7  # spaced out, looks realistic
        store_name = template[0].format(i=store_number)
        city = template[1]
        county = template[2]
        stores.append({
            "store_number": store_number,
            "store_name": store_name,
            "city": city,
            "county": county,
        })
    return pd.DataFrame(stores)


def generate_rows(rng: np.random.Generator, stores_df: pd.DataFrame) -> pd.DataFrame:
    """Generate all store x category x month rows."""
    years = list(range(YEAR_MIN, YEAR_MAX + 1))
    months = list(range(1, 13))

    rows = []
    for _, store in stores_df.iterrows():
        # Each store carries a subset of categories (8-15 per store)
        n_cats = rng.integers(8, 16)
        store_cats = rng.choice(
            len(CATEGORIES), size=n_cats, replace=False, p=CATEGORY_WEIGHTS
        )

        # Store-level baseline sales (log-normal, mean ~$15K/month for a top store)
        store_baseline = rng.lognormal(mean=9.6, sigma=0.4)

        for cat_idx in store_cats:
            category = CATEGORIES[cat_idx]
            # Category share of this store's sales
            cat_share = CATEGORY_WEIGHTS[cat_idx] * rng.uniform(0.7, 1.3)

            for year in years:
                for month in months:
                    # Base sales
                    base = store_baseline * cat_share * SEASONALITY[month]

                    # Year-over-year organic growth (~2% per year from baseline)
                    growth = 1.0 + 0.02 * (year - YEAR_MIN)
                    base *= growth

                    # COVID-era drift
                    is_covid = year in (2020, 2021)
                    if is_covid:
                        base *= COVID_SALES_MULTIPLIER
                        cat_mult = COVID_CATEGORY_SHIFT.get(category, 1.0)
                        base *= cat_mult

                    # Add noise (log-normal)
                    sigma = 0.25 * (COVID_VARIANCE_BOOST if is_covid else 1.0)
                    total_sales = base * rng.lognormal(mean=0, sigma=sigma)
                    total_sales = max(total_sales, 10.0)  # floor

                    # Derive other columns from total_sales
                    avg_bottle_price = rng.uniform(8.0, 45.0)
                    total_bottles = max(1, int(total_sales / avg_bottle_price * rng.uniform(0.8, 1.2)))
                    num_transactions = max(1, int(total_bottles * rng.uniform(0.3, 0.7)))
                    volume_per_bottle = rng.uniform(0.5, 1.75)
                    total_volume_liters = round(total_bottles * volume_per_bottle, 2)

                    rows.append({
                        "store_number": store["store_number"],
                        "store_name": store["store_name"],
                        "city": store["city"],
                        "county": store["county"],
                        "category_name": category,
                        "year": year,
                        "month": month,
                        "num_transactions": num_transactions,
                        "total_bottles": total_bottles,
                        "total_sales": round(total_sales, 2),
                        "total_volume_liters": total_volume_liters,
                        "avg_bottle_price": round(avg_bottle_price, 2),
                    })

    return pd.DataFrame(rows)


def split_and_save(df: pd.DataFrame) -> None:
    """Split into train / drift-test / holdout and write CSVs."""
    col_order = [
        "store_number", "store_name", "city", "county", "category_name",
        "year", "month",
        "num_transactions", "total_bottles", "total_sales",
        "total_volume_liters", "avg_bottle_price",
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
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("SYNTHETIC DATASET SUMMARY")
    print("=" * 60)
    print(f"Rows:    {len(df)}")
    print(f"Columns: {df.shape[1]}")
    print(f"Years:   {sorted(df['year'].unique())}")
    print(f"Stores:  {df['store_number'].nunique()}")
    print(f"Categories: {df['category_name'].nunique()}")
    print(f"\nTarget (total_sales) distribution:")
    print(df["total_sales"].describe().to_string())
    print("=" * 60)

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
    rng = np.random.default_rng(SEED)

    print("Generating synthetic Iowa Liquor Sales dataset ...")
    stores_df = build_stores(rng, NUM_STORES)
    df = generate_rows(rng, stores_df)

    print_summary(df)
    split_and_save(df)
    print("Done. Synthetic dataset files are in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
