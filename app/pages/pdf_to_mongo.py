from __future__ import annotations

import json
import pandas as pd
import streamlit as st

from app.services.mongodb import insert_pdf_data, fetch_pdf_data
from app.services.openai_client import chat_once
from app.utils.pdf import extract_text_from_pdf


def extract_important_info(text: str):
    prompt = f"""
    Extract important information from the following text and organize it into a structured format:

    {text[:2000]}

    Provide the output as a JSON object with appropriate keys and values.
    """
    response = chat_once([
        {"role": "system", "content": "You are a helpful assistant that extracts and structures information."},
        {"role": "user", "content": prompt},
    ])
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except Exception:
        return {"raw_content": content}


def pdf_to_mongodb_page():
    st.header("PDF to MongoDB Converter")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None and st.button("Process PDF and Store in MongoDB"):
        with st.spinner("Processing PDF and storing data..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            important_info = extract_important_info(pdf_text)
            inserted_id = insert_pdf_data(important_info)
            if inserted_id:
                st.success(f"Data inserted successfully! Document ID: {inserted_id}")
            else:
                st.error("Failed to insert data into MongoDB.")
            data = fetch_pdf_data(include_id=False)
            if data:
                st.subheader("Sample Data from MongoDB")
                st.dataframe(pd.DataFrame(data))
            else:
                st.info("No data to display from MongoDB.")
