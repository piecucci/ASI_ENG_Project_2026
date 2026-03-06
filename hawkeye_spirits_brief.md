# Hawkeye Spirits -- Business Scenario

## The Company

Hawkeye Spirits is a mid-size Iowa liquor distributor supplying 1,000+ retail stores across the state. They handle purchasing from vendors, warehousing, and distribution to stores.

## The Stakeholder

**Jordan Hayes, CFO.** Jordan needs monthly revenue predictions per store-category combination to optimize three areas:

- **Inventory purchasing**: Over-ordering ties up capital; under-ordering loses sales.
- **Staffing**: Warehouse and delivery staffing scales with predicted volume.
- **Cash flow planning**: Accurate forecasts prevent liquidity crunches.

## The Business Problem

Jordan currently uses last-year-same-month as a forecast baseline. It is wrong 40% of the time by more than 15%. Jordan wants an ML-based prediction that is consistently better than this naive baseline.

## The Five-Activity Arc

| Activity | Business Trigger |
|----------|-----------------|
| A1 -- Modularize | "Our data scientist built a model in a notebook. It works on her laptop. Make it production-ready." |
| A2 -- Containerize | "IT can't run Jupyter notebooks. Package this so it runs anywhere." |
| A3 -- Orchestrate | "We need this to run monthly with one command. And don't deploy a bad model." |
| A4 -- Track | "The data scientist wants to try 6 different configurations. Track them all and pick the winner." |
| A5 -- Drift | "COVID just hit. Our model is wrong. Fix it -- and make sure it fixes itself next time." |

## The Data

Iowa Liquor Sales aggregated to the store-category-month level. Approximately 49,000 rows across 12 columns. The prediction target is `total_sales`.

For full column definitions, splits, and known characteristics, see [`dataset/data_dictionary.md`](dataset/data_dictionary.md).

---

*Hawkeye Spirits is a fictional company created for educational purposes.*
