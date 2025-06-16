import os
from typing import List, Dict, Tuple
from .planning_agent import PlanningAgent
from .worker_agent import WorkerAgent
import logging
import re
from utils.web_search import duckduckgo_search

SUPPORTED_COMPANIES = [
    "TCS", "Infosys", "Wipro", "Tata Motors", "Mahindra & Mahindra",
    "Maruti Suzuki", "HDFC Bank", "HUL", "Reliance", "Adani Ports"
]

FALLBACK_MSG = (
    "I currently have no information about [{}]. Please choose from: "
    "TCS, Infosys, Wipro, Tata Motors, Mahindra & Mahindra, Maruti Suzuki, "
    "HDFC Bank, HUL, Reliance, Adani Ports."
)

class ExecutiveAgent:
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.worker_agent = WorkerAgent()
        self.supported_companies = set(SUPPORTED_COMPANIES)
        
        self.supported_companies_lower = [c.lower() for c in SUPPORTED_COMPANIES]
        self.supported_metrics = ["pe ratio", "eps", "roe", "debt-to-equity", "dividend yield", "cagr"]

    def parse_user_input(self, user_input: str) -> dict:
        """
        Parses user input string and returns dict:
        {
            'companies': List[str],
            'metrics': List[str],
            'intent': str  # one of 'single_metric', 'full_report', 'comparison', 'unknown'
        }
        """
        if not user_input:
            return {'companies': [], 'metrics': [], 'intent': 'unknown'}

        user_input_lower = user_input.lower()

        # Extract companies mentioned by simple substring matching
        companies_found = []
        for comp in self.supported_companies:
            if comp.lower() in user_input_lower:
                companies_found.append(comp)

        companies_found = list(set(companies_found))  # unique

        # Extract metrics by keyword matching
        metrics_found = []
        for metric in self.supported_metrics:
            if metric in user_input_lower:
                metrics_found.append(metric)

        # Determine intent heuristically
        intent = 'unknown'
        if len(companies_found) >= 2 and ('compare' in user_input_lower or 'better' in user_input_lower):
            intent = 'comparison'
        elif len(companies_found) == 1 and metrics_found:
            intent = 'single_metric'
        elif len(companies_found) == 1 and ('report' in user_input_lower or 'full' in user_input_lower):
            intent = 'full_report'
        elif len(companies_found) == 0:
            intent = 'unknown'
        else:
            intent = 'full_report'  # default fallback

        return {
            'companies': companies_found,
            'metrics': metrics_found,
            'intent': intent
        }

    def generate_report(self, companies: List[str], metrics: List[str]) -> Tuple[str, str]:
        """
        Main orchestration method.
        :param companies: List of company names (case insensitive)
        :param metrics: List of financial metric strings
        :return: Tuple(HTML report as str, path to PDF file)
        """

        companies = [c.strip() for c in companies if c.strip()]
        valid_companies = []
        invalid_companies = []
        for c in companies:
            # Normalize company names (case-insensitive)
            c_norm = c.title()  # Or use another normalization consistent with your corpus
            if c_norm in self.supported_companies:
                valid_companies.append(c_norm)
            else:
                invalid_companies.append(c)

        if len(valid_companies) < 1:
            # No supported companies found, try fallback for first unknown company
            fallback_text = duckduckgo_search(invalid_companies[0]) if invalid_companies else "No valid company input."
            # Create a minimal report with fallback text only
            html_report = self.worker_agent.create_full_report([], [], fallback_text=fallback_text)
            return html_report, None

        # Process known companies normally
        company_data = []
        for company in valid_companies:
            try:
                data_block = self.planning_agent.analyze_company(company, metrics)
                company_data.append(data_block)
            except Exception as e:
                logging.error(f"Error analyzing {company}: {e}")
                company_data.append({
                    "company": company,
                    "metrics": {},
                    "rag_summary": "Data unavailable due to error.",
                    "risk_assessment": "N/A"
                })

        fallback_text = None
        if invalid_companies:
            # Optionally, perform web search for unknown companies and append
            fallback_results = []
            for unknown in invalid_companies:
                fallback_results.extend(duckduckgo_search(unknown))
            if fallback_results:
                fallback_text = "\n\n".join(
                    [f"{r['title']}: {r['snippet']} (Link: {r['url']})" for r in fallback_results]
                )

        # Generate full report with optional fallback text
        html_report = self.worker_agent.create_full_report(company_data, metrics, fallback_text=fallback_text)
        pdf_path = self.worker_agent.convert_html_to_pdf(html_report)

        return html_report, pdf_path
