# import weasyprint
import os
import tempfile
from utils.chart_generator import generate_metric_bar_chart
from utils.gemma_client import GemmaClient
import requests
import logging
from dotenv import load_dotenv
import datetime

load_dotenv()  # Load env variables from .env

# Instantiate Gemma client globally
gemma_client = GemmaClient()

def generate_text(prompt: str, max_tokens=300):
    try:
        return gemma_client.generate_text(prompt)
    except Exception as e:
        logging.error(f"Gemma generation API call failed: {e}")
        return "Generation unavailable due to API error."

class WorkerAgent:

    def create_full_report(self, company_data_list, metrics, fallback_text=None):
        """
        Generate the full HTML report.

        :param company_data_list: List of dicts with company info (company, rag_summary, metrics, risk_assessment)
        :param metrics: List of requested financial metrics
        :param fallback_text: Optional string with fallback web search info for unknown companies
        :return: HTML report string
        """

        # Executive summary
        exec_summary_text = self._generate_executive_summary(company_data_list)

        # Interpretation (only if metrics and multiple companies)
        if metrics and len(company_data_list) > 1:
            combined_metrics = []
            for data in company_data_list:
                metrics_text = f"{data['company']}: " + ", ".join(
                    f"{m}={data['metrics'].get(m, 'N/A')}" for m in metrics
                )
                combined_metrics.append(metrics_text)
            interpretation_prompt = (
                "Please provide a detailed and professional analysis of the following financial metrics comparison:\n\n"
                + "\n".join(combined_metrics)
                + "\n\nInterpretation:"
            )
            interpretation_text = generate_text(interpretation_prompt, max_tokens=400)
        else:
            interpretation_text = "Not enough data for financial interpretation."

        # Company Profiles HTML
        company_profiles_html = "<h2>Company Profiles</h2>\n"
        for data in company_data_list:
            company_name = data.get("company", "Unknown Company")
            rag_summary = data.get("rag_summary", "").strip()
            if not rag_summary:
                rag_summary = "No detailed information available."

            detailed_profile_prompt = (
                f"Based on the following summary about {company_name}, write a detailed and extensive company profile, "
                f"covering history, products/services, market presence, financial highlights, leadership, and strategic plans:\n\n"
                f"{rag_summary}\n\nDetailed Profile:"
            )
            detailed_profile = generate_text(detailed_profile_prompt, max_tokens=3000)

            company_profiles_html += f"<h3>{company_name}</h3><p>{detailed_profile}</p>\n"

        # Financial Charts - generate for each metric
        financial_charts_html = "<h2>Financial Charts</h2>\n"
        if metrics:
            for metric in metrics:
                chart_html = generate_metric_bar_chart(company_data_list, metric)
                financial_charts_html += f"<h3>{metric}</h3>\n{chart_html}\n"
        else:
            financial_charts_html += "<p>No financial metrics selected for chart generation.</p>"

        # Investment Recommendations section
        investment_recommendations_html = "<h2>Investment Recommendations</h2>\n"
        for data in company_data_list:
            company_name = data.get("company", "Unknown Company")
            rag_summary = data.get("rag_summary", "").strip()
            if not rag_summary:
                rag_summary = "No detailed information available."
            recommendation = self._generate_investment_recommendation(company_name, rag_summary)
            investment_recommendations_html += f"<h3>{company_name}</h3><p>{recommendation}</p>\n"

        # Market Outlook placeholder
        market_outlook_html = "<h2>Market Outlook</h2><p>[Market news and outlook here]</p>"

        # Optional fallback section
        fallback_html = ""
        if fallback_text:
            fallback_html = f"""
            <hr>
            <section id="fallback-info">
                <h2>Additional Information from Web Search</h2>
                <p>{fallback_text}</p>
            </section>
            """

        # Assemble full HTML report
        html_report = f"""
        <html>
        <head>
            <title>Investment Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #121212;
                    color: white;
                }}
                h1, h2, h3 {{
                    color: white;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: white;
                }}
                hr {{
                    margin: 40px 0;
                    border-color: #444;
                }}
            </style>
        </head>
        <body>
            <h1>Investment Report</h1>
            <hr>
            <section id="executive-summary">
                <h2>Executive Summary</h2>
                <p>{exec_summary_text}</p>
            </section>
            <hr>
            <section id="company-profiles">
                {company_profiles_html}
            </section>
            <hr>
            <section id="financial-charts">
                {financial_charts_html}
            </section>
            <hr>
            <section id="investment-recommendations">
                {investment_recommendations_html}
            </section>
            <hr>
            <section id="interpretation">
                <h2>Interpretation</h2>
                <p>{interpretation_text}</p>
            </section>
            <hr>
            <section id="market-outlook">
                {market_outlook_html}
            </section>
            {fallback_html}
        </body>
        </html>
        """

        return html_report

    def _generate_executive_summary(self, company_data_list):
        if not company_data_list:
            return "No company data available to summarize."

        company_texts = []
        for data in company_data_list:
            company_name = data.get("company", "Unknown Company")
            rag_summary = data.get("rag_summary", "").strip()
            if not rag_summary:
                rag_summary = f"No detailed information available for {company_name}."
            company_texts.append(f"{company_name}:\n{rag_summary}\n")

        prompt = (
            "\n\n".join(company_texts) +
            "\n\nPlease write a comprehensive, detailed, and thorough executive summary that covers all major aspects, including company history, recent performance, market position, strategic initiatives, risks, opportunities, and future outlook. "
            "The summary should be verbose and at least several hundred lines long.\nSummary:"
        )
        return generate_text(prompt, max_tokens=3000)

    def _generate_interpretation(self, company_data_list, metrics):
        combined_metrics = []
        for data in company_data_list:
            metric_pairs = []
            for m in metrics:
                val = data['metrics'].get(m)
                if val is None or (not val and val != 0):
                    val = 'N/A'
                metric_pairs.append(f"{m}={val}")
            metrics_text = f"{data['company']}: " + ", ".join(metric_pairs)
            combined_metrics.append(metrics_text)

        prompt = (
            "Please provide a detailed and professional analysis of the following financial metrics comparison:\n\n"
            + "\n".join(combined_metrics)
            + "\n\nInterpretation:"
        )
        logging.debug(f"Interpretation prompt:\n{prompt}")

        return generate_text(prompt, max_tokens=600)

    def _generate_investment_recommendation(self, company_name, rag_summary):
        prompt = (
            f"Based on the following summary about {company_name}, provide a clear one-line investment recommendation "
            f"indicating whether one should invest or not, with a concise reason:\n\n"
            f"{rag_summary}\n\nRecommendation:"
        )
        return generate_text(prompt, max_tokens=60)

    def convert_html_to_pdf(self, html_content):
        # os.makedirs("outputs/reports", exist_ok=True)
        # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # pdf_path = f"outputs/reports/investment_report_{timestamp}.pdf"

        # try:
        #     weasyprint.HTML(string=html_content).write_pdf(pdf_path)
        #     return pdf_path
        # except Exception as e:
        #     logging.error(f"PDF generation failed: {e}")
        return None
