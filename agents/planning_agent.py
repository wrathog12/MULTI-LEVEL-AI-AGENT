import yfinance as yf
from utils.rag_retriever import RAGRetriever
from utils.gemma_client import GemmaClient  # New import for Gemma
import os
import logging
import requests
from typing import List, Dict
from dotenv import load_dotenv
import time

load_dotenv()  # Load environment variables from .env file

# Instantiate Gemma client globally
gemma_client = GemmaClient()

def summarize_text(prompt: str) -> str:
    full_prompt = f"Summarize the following financial text in a concise manner:\n\n{prompt}"
    return gemma_client.summarize(full_prompt)

class PlanningAgent:
    def __init__(self):
        self.rag_retriever = RAGRetriever()

    def fetch_financial_data(self, ticker: str, metrics: List[str]) -> Dict:
        result = {}
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if "PE Ratio" in metrics:
                result["PE Ratio"] = info.get("trailingPE")
            if "Debt-to-Equity" in metrics:
                result["Debt-to-Equity"] = info.get("debtToEquity")
            if "EPS" in metrics:
                result["EPS"] = info.get("trailingEps")
            if "ROE" in metrics:
                result["ROE"] = info.get("returnOnEquity")
            if "Dividend Yield" in metrics:
                dy = info.get("dividendYield")
                result["Dividend Yield"] = dy * 100 if dy is not None else None
            if "CAGR" in metrics:
                result["CAGR"] = None  # Not directly available via yfinance
            # Add other metrics similarly...
            time.sleep(2)  # To avoid hitting API rate limits
        except Exception as e:
            logging.error(f"Failed to fetch financial data for {ticker}: {e}")
        return result

    def analyze_company(self, company: str, metrics: List[str]) -> Dict:
        financial_data = self.fetch_financial_data(company, metrics)

        raw_texts = self.rag_retriever.retrieve(company, top_k=3)

        prompt = (
            f"Summarize the profile, risks, and future outlook of {company} based on the following texts:\n\n"
            + "\n\n".join(raw_texts)
            + "\n\nSummary:"
        )

        rag_summary = summarize_text(prompt)  # Updated to use Gemma

        risk = "Low risk"
        dte = financial_data.get("Debt-to-Equity")
        if dte is not None and dte > 100:
            risk = "High risk due to high Debt-to-Equity ratio."

        return {
            "company": company,
            "metrics": financial_data,
            "rag_summary": rag_summary,
            "risk_assessment": risk
        }
