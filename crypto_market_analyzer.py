import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch


# User-Agent header to mimic browser traffic
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

def fetch_crypto_data(limit=20):
    """
    Fetches top cryptocurrency data from CoinMarketCap.
    Returns list of dictionaries containing name, symbol, price, market cap, and 24h change.
    """
    url = "https://coinmarketcap.com/" 
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    crypto_data = []
    rows = soup.select('table tbody tr')[:limit]

    for row in rows:
        cols = row.find_all('td')

        if len(cols) < 7:
            continue  # Skip malformed rows

        name_tag = cols[2].find('p')
        symbol = cols[2].find('span', class_='coin-item-symbol').text.strip() if cols[2].find('span', class_='coin-item-symbol') else "N/A"
        price = float(cols[3].text.replace('$', '').replace(',', '').strip())
        market_cap = cols[6].text.strip()
        change_24h = cols[7].text.strip()

        crypto_data.append({
            'Name': name_tag.text.strip() if name_tag else "Unknown",
            'Symbol': symbol,
            'Price (USD)': price,
            'Market Cap': market_cap,
            '24h Change': change_24h
        })

    return crypto_data


def analyze_crypto_data(data):
    """
    Performs basic analysis on the fetched cryptocurrency data.
    """
    df = pd.DataFrame(data)

    # Convert Price (USD) to numeric
    df['Price (USD)'] = pd.to_numeric(df['Price (USD)'], errors='coerce')

    summary = {
        'Total Cryptocurrencies': len(df),
        'Top 5 by Market Cap': df[['Name', 'Market Cap']].head(5).to_dict(),
        'Average Price (USD)': round(df['Price (USD)'].mean(), 2),
        'Highest Priced Coin': df.loc[df['Price (USD)'].idxmax()]['Name'],
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return df, summary


def save_data(dataframe, summary):
    """
    Saves raw data and summary to CSV, JSON, and a styled PDF format.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Save CSV
    dataframe.to_csv(f'{output_dir}/crypto_data_{timestamp}.csv', index=False)

    # Save JSON
    with open(f'{output_dir}/crypto_summary_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=4)

    # Generate PDF
    pdf_path = f"{output_dir}/crypto_summary_{timestamp}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = styles['Title']
    elements.append(Paragraph("Cryptocurrency Market Analysis Report", title_style))
    elements.append(Spacer(1, 24))

    # Timestamp
    date_style = styles['Normal']
    elements.append(Paragraph(f"Generated on: {summary['Timestamp']}", date_style))
    elements.append(Spacer(1, 24))

    # Summary Section
    elements.append(Paragraph("📊 Summary Statistics", styles['Heading2']))
    summary_text = [
        f"Total Cryptocurrencies: {summary['Total Cryptocurrencies']}",
        f"Average Price (USD): ${summary['Average Price (USD)']}",
        f"Highest Priced Coin: {summary['Highest Priced Coin']}"
    ]
    for line in summary_text:
        elements.append(Paragraph(line, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Top 5 Coins
    elements.append(Paragraph("🏆 Top 5 Cryptocurrencies by Market Cap", styles['Heading2']))
    top_coins = summary['Top 5 by Market Cap']['Name']
    for i, coin in enumerate(top_coins.values()):
        elements.append(Paragraph(f"{i+1}. {coin}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Table of Data
    elements.append(Paragraph("📄 Cryptocurrency Data Table", styles['Heading2']))
    data_table = [dataframe.columns.tolist()] + dataframe.values.tolist()
    table = Table(data_table)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)

    # Build PDF
    doc.build(elements)

    print(f"\n✅ Raw data saved to {output_dir}/crypto_data_{timestamp}.csv")
    print(f"✅ Summary saved to {output_dir}/crypto_summary_{timestamp}.json")
    print(f"✅ Styled PDF report saved to {output_dir}/crypto_summary_{timestamp}.pdf")


if __name__ == "__main__":
    print("🚀 Fetching live cryptocurrency market data...")
    raw_data = fetch_crypto_data(limit=20)

    if raw_data:
        print(f"📊 Analyzing data for {len(raw_data)} cryptocurrencies...\n")
        df, summary = analyze_crypto_data(raw_data)

        print("📈 Summary:")
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  - {k}: {v}")
            else:
                print(f"{key}: {value}")

        save_data(df, summary)
    else:
        print("❌ No data was retrieved.")