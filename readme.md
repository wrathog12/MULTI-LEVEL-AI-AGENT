````
# Multi-Level AI Investment Report Generator

## Project Overview

This project is a modular AI-powered system designed to generate comprehensive investment reports for selected companies. It combines live financial data, retrieval-augmented knowledge, and large language models to produce detailed summaries, company profiles, charts, and investment recommendations — all accessible through an interactive Streamlit web application.

---

## Features

- Select companies and financial metrics from predefined lists.
- Fetches real-time financial data via Yahoo Finance (`yfinance`).
- Uses Google Gemini's Gemma model for natural language summarization and report generation.
- Generates interactive financial charts with Plotly.
- Produces consolidated HTML reports with executive summaries, detailed profiles, and investment advice.
- Supports fallback web search for unknown companies.
- Lightweight, easy-to-use web UI with Streamlit.

---

## Tech Stack

- Python 3.10+
- Streamlit for frontend
- Google Gemini API (Gemma 3 27B IT) for AI generation
- yfinance for financial data
- Plotly for visualization
- python-dotenv for environment variable management

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-investment-report.git
cd ai-investment-report
````

### 2. Create and activate a Python virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env` file

Create a `.env` file in the project root with the following content:

```
Gemini_API_TOKEN=your_google_gemini_api_key_here
```

Replace `your_google_gemini_api_key_here` with your actual API key obtained from Google Cloud Console or the Gemini API provider.

### 5. Run the Streamlit app

```bash
streamlit run app.py
```

Open the URL displayed in the terminal (usually `http://localhost:8501`) in your browser.

---

## About the AI Model

This project uses Google Gemini's **Gemma 3 27B IT** model accessed through the `google-genai` Python SDK. Gemma is a powerful large language model specialized for instruction-following and text generation tasks. It handles:

* Summarization of financial and textual data.
* Generation of detailed company profiles and investment recommendations.
* Comparative financial analysis and interpretation.

Gemma replaces the previously used Hugging Face models to provide improved quality and API efficiency.

---

## Project Structure

* `app.py`: Streamlit user interface entry point.
* `agents/`: Contains multi-level agent classes managing planning, working, and executive logic.
* `utils/`: Helper utilities including `gemma_client.py` for API integration and `chart_generator.py` for visualization.
* `.env`: Stores your Gemini API key securely.
* `requirements.txt`: Python dependencies.

---

## Key Learnings & Notes

* Modular agent design separates concerns and simplifies maintenance.
* Lightweight NLP parsing replaces heavy libraries for better performance.
* Cloud-based LLM APIs enable rich generation without heavy local compute.
* Plotly integration adds dynamic, interactive financial charts.
* Error handling and fallback web search improve robustness.

---

## Troubleshooting

* Ensure your Python environment matches the versions in `requirements.txt`.
* Confirm your Gemini API key is valid and correctly set in `.env`.
* If `faiss` or other dependencies fail to install, check compatibility with your OS.
* For Streamlit UI issues, verify your browser allows local connections.

---

## License

[MIT License](LICENSE)

```
```
