from __future__ import annotations

import json

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.services.openai_client import chat_once
from app.utils.pdf import extract_text_from_pdf


def format_large_number(num):
    if num is None:
        return "N/A"
    if abs(num) >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:.2f}M"
    elif abs(num) >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:,.2f}"


def parse_financial_data(text: str):
    prompt = f"""
    Extract the following financial information from the given text:
    - Total revenue (in dollars)
    - Revenue growth (percentage)
    - Operating profit (in dollars)
    - Operating margin (percentage)
    - Net income (in dollars)
    - Earnings per share (EPS) (in dollars)
    - Operating cash flow (in dollars)
    - Revenue breakdown: Provide a detailed breakdown of revenue by all available categories, segments, or product lines. Include ALL subcategories mentioned in the report.

    Text: {text}

    Provide the output as a JSON object with appropriate keys and values. 
    If you can't find a specific piece of information, use null for its value.

    IMPORTANT: 
    1. For all monetary values (revenue, profit, income, cash flow):
       - If the report states the values are in millions or billions, convert them to the full number.
       - For example, if it says "$70.01 billion", the value should be 70010000000.
       - If it says "$80.46 million", the value should be 80460000.
    2. Ensure all monetary values are in whole numbers (no decimals).
    3. Percentages should be in decimal form (e.g., 15% should be 15, not 0.15).
    4. For the revenue breakdown:
       - Include ALL categories and subcategories mentioned in the report.
       - This might include terms like "Family of Apps", "Reality Labs", "Advertising", "Other revenue", etc.
       - Provide this as a nested dictionary if there are subcategories.
       - Use the same scale as the total revenue.
    5. The EPS should be in dollars and cents (e.g., 4.88 for $4.88 per share).
    6. If operating profit is not explicitly stated, it may be referred to as "Income from operations" or similar terms.

    Be extremely thorough in extracting all revenue categories and subcategories. Do not omit any breakdown information provided in the report.

    Reply with the JSON object only. Don't give any explanations or comments. Just provide the structured JSON data.
    """

    try:
        response = chat_once([
            {"role": "system", "content": "You are a highly skilled financial analyst AI that extracts and structures financial data accurately and comprehensively."},
            {"role": "user", "content": prompt},
        ])
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        required_keys = [
            "total_revenue",
            "revenue_growth",
            "operating_profit",
            "operating_margin",
            "net_income",
            "earnings_per_share",
            "operating_cash_flow",
            "revenue_breakdown",
        ]
        for k in required_keys:
            data.setdefault(k, None)
        return data
    except Exception:
        return None


def business_metrics_dashboard():
    st.title("Strategic Financial Intelligence Hub")
    uploaded_file = st.file_uploader("Upload your quarterly financial report (PDF)", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner(" Processing the PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            financial_data = parse_financial_data(text)

        if financial_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    label="Total Revenue",
                    value=format_large_number(financial_data["total_revenue"]),
                    delta=f"{financial_data['revenue_growth']}% YoY" if financial_data["revenue_growth"] is not None else None,
                )
            with col2:
                st.metric(
                    label="Operating Profit",
                    value=format_large_number(financial_data["operating_profit"]),
                    delta=f"Margin: {financial_data['operating_margin']}%" if financial_data["operating_margin"] is not None else None,
                )
            with col3:
                st.metric(
                    label="Net Income",
                    value=format_large_number(financial_data["net_income"]),
                    delta=f"EPS: ${financial_data['earnings_per_share']:.2f}" if financial_data["earnings_per_share"] is not None else "No EPS available.",
                )
            with col4:
                st.metric(
                    label="Operating Cash Flow",
                    value=format_large_number(financial_data["operating_cash_flow"]),
                    delta=f"{financial_data['operating_cash_flow']/financial_data['total_revenue']*100:.1f}% of Rev" if financial_data["operating_cash_flow"] is not None and financial_data["total_revenue"] is not None else None,
                )

            st.subheader("Revenue Breakdown by Segments")
            if financial_data["revenue_breakdown"]:
                from app.utils.json_tools import flatten_dict

                flattened_breakdown = flatten_dict(financial_data["revenue_breakdown"])
                fig = px.pie(
                    values=list(flattened_breakdown.values()),
                    names=list(flattened_breakdown.keys()),
                    title="Revenue by Segment",
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No revenue breakdown data available.")

            st.subheader("Earnings Per Share (EPS)")
            if financial_data["earnings_per_share"] is not None:
                fig_eps = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=financial_data["earnings_per_share"],
                        number={"prefix": "$"},
                        title={"text": "Earnings Per Share"},
                    )
                )
                st.plotly_chart(fig_eps, use_container_width=True)
            else:
                st.info("No EPS available.")

            st.subheader("Key Financial Metrics")
            if (
                financial_data["total_revenue"] is not None
                and financial_data["operating_profit"] is not None
                and financial_data["net_income"] is not None
            ):
                fig_metrics = go.Figure(
                    data=[
                        go.Bar(name="Total Revenue", x=["Total"], y=[financial_data["total_revenue"]]),
                        go.Bar(name="Operating Profit", x=["Total"], y=[financial_data["operating_profit"]]),
                        go.Bar(name="Net Income", x=["Total"], y=[financial_data["net_income"]]),
                    ]
                )
                fig_metrics.update_layout(barmode="group", title="Key Financial Metrics")
                st.plotly_chart(fig_metrics, use_container_width=True)
            else:
                st.info("No key financial metrics available.")
        else:
            st.error("Failed to extract financial data from the uploaded report.")
    else:
        st.info("Please upload a quarterly financial report (PDF) to view the dashboard.")
