import plotly.graph_objects as go
import pandas as pd
import logging

def generate_metric_bar_chart(company_data_list, metric):
    """
    Creates a Plotly bar chart comparing companies on a given metric.
    company_data_list: List of dicts with keys 'company' and 'metrics'
    metric: string, e.g. "PE Ratio"
    Returns: HTML div string
    """
    companies = []
    values = []

    for data in company_data_list:
        val = data["metrics"].get(metric)
        if val is not None:
            companies.append(data["company"])
            values.append(val)

    if not companies:
        logging.warning(f"No data available for metric: {metric}")
        return "<p>No data available for {}</p>".format(metric)

    fig = go.Figure(data=[go.Bar(x=companies, y=values)])
    fig.update_layout(
        title=f"Comparison of {metric} across Companies",
        xaxis_title="Company",
        yaxis_title=metric,
        template="plotly_white"
    )
    return fig.to_html(full_html=False)
