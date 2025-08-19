from __future__ import annotations

import json
import streamlit as st
from json2table import convert

from app.services.mongodb import fetch_pdf_data


def db_image_page():
    st.header("MongoDB Document Viewer")
    data = fetch_pdf_data(include_id=False)

    if not data:
        st.info("No data available in MongoDB.")
        return

    document_ids = [f"Document {i + 1}" for i in range(len(data))]
    selected_document = st.selectbox("Select a document to view:", document_ids)
    selected_index = document_ids.index(selected_document)
    st.subheader(selected_document)

    if "raw_content" in data[selected_index]:
        json_string = data[selected_index]["raw_content"].replace("```json", "").strip("'''\"")
        if json_string.endswith("```"):
            json_string = json_string[:-3]
        try:
            json_data = json.loads(json_string)
            st.success("JSON string parsed successfully:")
            table = convert(json_data)
            st.write(table, unsafe_allow_html=True)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON string: {e}")
            st.write("JSON string that failed to parse:")
            st.code(json_string)
    else:
        st.json(data[selected_index])

    st.markdown("---")
