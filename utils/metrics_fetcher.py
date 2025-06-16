import yfinance as yf

METRIC_KEY_MAP = {
    "pe ratio": "PE Ratio",
    "eps": "EPS",
    "roe": "ROE",
    "debt-to-equity": "Debt-to-Equity",
    "dividend yield": "Dividend Yield",
    "cagr": "CAGR"
}

def fetch_financial_metrics(ticker: str, metrics: list):
    result = {}
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        for metric in metrics:
            key = METRIC_KEY_MAP.get(metric.lower())
            if not key:
                continue
            if key == "PE Ratio":
                result[key] = info.get("trailingPE")
            elif key == "EPS":
                result[key] = info.get("trailingEps")
            elif key == "ROE":
                result[key] = info.get("returnOnEquity")
            elif key == "Debt-to-Equity":
                result[key] = info.get("debtToEquity")
            elif key == "Dividend Yield":
                dy = info.get("dividendYield")
                result[key] = dy * 100 if dy is not None else None
            elif key == "CAGR":
                result[key] = None  # Implement CAGR if possible
    except Exception as e:
        print(f"Error fetching metrics for {ticker}: {e}")
    return result
