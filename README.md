# US Consumer Spending Analysis

An interactive financial analytics dashboard exploring 13 million transactions across 1,219 users from a synthetic US banking dataset covering 2010–2019.

---

## Dashboard Pages

| Page | Description |
|---|---|
| **Spending Overview** | Total spend, transaction volume, and monthly trends with 3-month and 12-month moving averages |
| **Spending by Category** | Top merchant categories by transaction volume and average transaction size, with historical spending trends |
| **Error & Fraud Analysis** | Transaction error types, their fraud rates, and which merchant categories are most affected by fraud |
| **Forecasting** | SARIMA time series forecasting trained on 2010–2018 data, validated against 2019 (MAPE: 0.65%), with a category-level forecast dropdown |

---

## Technical Stack

- **Python** - Pandas, Statsmodels, Scikit-learn, Plotly, Streamlit
- **SQL** - SQLite with complex queries including window functions, CTEs, and aggregations
- **SARIMA** - Seasonal time series forecasting with automated stationarity testing
- **SQLite** - Single-file database housing 13M+ records across 5 tables

---

## Running Locally

1. Clone the repository
2. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets)
3. Place the files in a `data/` folder in the repo root
4. Run `python setup_db.py` to build the database
5. Run `python precompute.py` to generate precomputed fraud aggregations
6. Run `streamlit run app.py` to launch the dashboard

---

## Demo

*Video walkthrough coming soon*