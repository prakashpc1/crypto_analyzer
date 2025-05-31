# Crypto Market Analyzer – Enhanced PDF Output

A Python script that scrapes real-time cryptocurrency data from [CoinMarketCap](https://coinmarketcap.com),  performs basic analysis, and exports results to **CSV**, **JSON**, and a **styled PDF report**.

## 🧠 Features
- Scrapes top cryptocurrency data including name, price, market cap, and 24h change.
- Uses `pandas` for data analysis.
- Exports clean data and summary statistics in **CSV**, **JSON**, and **PDF** formats.
- Generates a **colorful, human-readable PDF** using `reportlab`.
- Includes:
  - Summary stats
  - Top 5 cryptocurrencies
  - Full data table with styling

## 📦 Prerequisites
Make sure you have the following installed:

- Python 3.x
- Required libraries:
  ```bash
  pip install requests beautifulsoup4 pandas reportlab
