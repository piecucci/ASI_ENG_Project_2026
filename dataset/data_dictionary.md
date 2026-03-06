# Data Dictionary: Iowa Liquor Sales (Aggregated)

## Granularity

One row = one **store** + one **category** + one **month**. Each row aggregates all transactions for a given store-category-month combination.

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `store_number` | int | Unique store identifier |
| `store_name` | string | Name of the retail store |
| `city` | string | City where the store is located |
| `county` | string | Iowa county |
| `category_name` | string | Liquor category (see top categories below) |
| `year` | int | Calendar year |
| `month` | int | Calendar month (1--12) |
| `num_transactions` | int | Count of transactions for that store-category-month |
| `total_bottles` | int | Total bottles sold |
| `total_sales` | float | **TARGET** -- Total dollar sales (this is the value we predict) |
| `total_volume_liters` | float | Total volume sold in liters |
| `avg_bottle_price` | float | Average price per bottle |

### Drift-test only

| Column | Type | Description |
|--------|------|-------------|
| `year_month` | string | Year and month formatted as `"YYYY-MM"` (e.g., `"2020-01"`). Present only in the drift-test split. |

## Top 10 Categories (by frequency)

1. VODKA 80 PROOF
2. CANADIAN WHISKIES
3. WHISKEY LIQUEUR
4. SPICED RUM
5. STRAIGHT BOURBON WHISKIES
6. BLENDED WHISKIES
7. TEQUILA
8. IMPORTED VODKA
9. TENNESSEE WHISKIES
10. SCOTCH WHISKIES

## Data Splits

| Split | Years | Rows |
|-------|-------|------|
| Train | 2017--2019 | 20,916 |
| Drift | 2020--2021 | 13,944 |
| Holdout | 2022--2023 | 13,944 |
| **Total** | **2017--2023** | **48,804** |

## Known Characteristics

- **COVID drift**: The 2020--2021 period shows distributional shift due to the COVID-19 pandemic, making it a natural drift-detection test set.
- **Log-normal distributions**: Sales and volume features follow approximately log-normal distributions.
- **Seasonal patterns**: Monthly sales exhibit clear seasonality (e.g., higher sales in December).

**Scale**: 50 stores, 20 liquor categories.
