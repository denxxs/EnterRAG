from __future__ import annotations

import json
import logging

import streamlit as st

from app.services.mongodb import fetch_pdf_data, update_pdf_document
from app.services.openai_client import chat_once

logger = logging.getLogger(__name__)


def generate_modified_json(document, user_input):
    prompt = f"""
    Given the following MongoDB document:
    {json.dumps(document, indent=2)}

    And the user's request to modify it:
    {user_input}

    Generate the modified JSON document. Return only the modified JSON, without any explanation or additional text.
    Ensure that you're modifying the correct fields and using appropriate data types.
    If a field doesn't exist and needs to be added, add it to the appropriate place in the JSON structure.
    If a field needs to be removed, remove it entirely.
    Preserve any fields that don't need modification.
    """

    try:
        response = chat_once([
            {"role": "system", "content": "You are a helpful assistant that modifies JSON documents based on user instructions."},
            {"role": "user", "content": prompt},
        ])
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        logger.exception("Error in generate_modified_json")
        raise


def edit_mongodb_document():
    st.subheader("Edit MongoDB Document")

    data = fetch_pdf_data(include_id=True)
    if not data:
        st.info("No data available in MongoDB.")
        return

    import pandas as pd

    df = pd.DataFrame(data)
    st.dataframe(df)

    selected_index = st.selectbox("Select a document to edit", range(len(data)), format_func=lambda i: f"Document {i+1}")
    selected_doc = data[selected_index]

    st.json(selected_doc)

    user_input = st.text_area("Describe the changes you want to make to this document:")

    if st.button("Apply Changes"):
        if user_input:
            try:
                modified_json = generate_modified_json(selected_doc, user_input)
                st.subheader("Modified JSON:")
                st.write(modified_json)

                if st.button("Confirm and Update MongoDB"):
                    ok = update_pdf_document(str(selected_doc["_id"]), modified_json)
                    if ok:
                        st.success("Document updated successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to update the document in MongoDB.")
            except Exception as e:
                logger.exception("Error in edit_mongodb_document")
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please describe the changes you want to make.")
