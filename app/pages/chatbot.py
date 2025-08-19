from __future__ import annotations

import re
import streamlit as st

from app.services.chroma_store import query, add_texts
from app.services.openai_client import stream_chat
from app.utils.pdf import extract_text_from_pdf, chunk_text


class AIChatbot:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def generate_response(self, user_input: str):
        docs = query(self.collection_name, user_input, k=3)
        context = " ".join(docs)
        return stream_chat([
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Formatting rules: respond in plain text; do not use markdown emphasis or code blocks; "
                    "avoid underscores and asterisks; use simple '-' bullets; put a space between numbers and units/words; "
                    "format quarters as 'Q2 2024' (quarter letter + digit, space, 4-digit year); use en/em dashes with spaces around them."
                ),
            },
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_input}"},
        ])


def _fix_markdown_spacing(text: str) -> str:
    """Clean up common markdown spacing glitches in model output.

    - Insert spaces between numbers and words (e.g., 40billion -> 40 billion)
    - Insert spaces between words and numbers (e.g., rangeof35 -> range of 35)
    - Normalize spaces around dashes in ranges (e.g., 37-40 -> 37 — 40)
    - Ensure spaces around italic segments like *text* or _text_
    """
    if not text:
        return text
    # Remove markdown emphasis that causes 'cursive' rendering
    # Unwrap bold/italic markers while preserving inner text
    text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)  # **bold** -> bold
    text = re.sub(r"\*([^\*]+)\*", r"\1", text)        # *italic* -> italic
    text = re.sub(r"__([^_]+)__", r"\1", text)            # __bold__ -> bold
    text = re.sub(r"_([^_]+)_", r"\1", text)              # _italic_ -> italic

    # Number-letter and letter-number boundaries
    text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    # Rejoin common financial shorthands correctly
    # Q + digit + optional spaces + 4-digit year -> 'Q{digit} {year}'
    text = re.sub(r"\bQ\s*([1-4])\s*(20\d{2})\b", r"Q\1 \2", text)
    # Avoid splitting 'Q2' into 'Q 2'
    text = re.sub(r"\bQ\s+([1-4])\b", r"Q\1", text)
    # Normalize dash spacing in ranges
    text = re.sub(r"\s*[–—-]\s*", " — ", text)
    # Neutralize stray underscores inside words (not bullets)
    text = re.sub(r"(?<=\w)_(?=\w)", " ", text)
    # Collapse multiple spaces but preserve newlines
    text = re.sub(r" {2,}", " ", text)
    return text


def manage_collections_ui():
    st.header("Manage Collections")
    from app.services.chroma_store import get_client

    client = get_client()
    collections = [c.name for c in client.list_collections()]

    task = st.radio("What would you like to do?", ("Add Collection", "Modify Collection", "Delete Collection"))

    if task == "Add Collection":
        st.subheader("Add New Collection")
        new_collection_name = st.text_input("Collection Name")
        uploaded_files = st.file_uploader("Upload PDF Files", type="pdf", accept_multiple_files=True)
        if st.button("Add Collection"):
            if new_collection_name and uploaded_files:
                _add_files_to_collection(new_collection_name, uploaded_files)

    elif task == "Modify Collection":
        st.subheader("Modify Existing Collection")
        selected_collection = st.selectbox("Select a Collection", collections)
        if selected_collection:
            st.write("Add new files:")
            new_files = st.file_uploader(f"Add PDF Files to {selected_collection}", type="pdf", accept_multiple_files=True)
            if st.button("Add Files") and new_files:
                _add_files_to_collection(selected_collection, new_files)

            st.write("Delete existing files:")
            existing_files = _list_files_in_collection(selected_collection)
            if existing_files:
                files_to_delete = st.multiselect("Select files to delete", existing_files)
                if st.button("Delete Selected Files") and files_to_delete:
                    _delete_files_from_collection(selected_collection, files_to_delete)
                    st.success("Files deleted. Please refresh the page to see the updated file list.")
                    st.button("Refresh")
            else:
                st.info("No files found in this collection.")

    elif task == "Delete Collection":
        st.subheader("Delete Collection")
        selected_collection = st.selectbox("Select a Collection to Delete", collections)
        if st.button("Delete Collection") and selected_collection:
            from app.services.chroma_store import get_client

            client.delete_collection(name=selected_collection)
            st.success(f"Deleted collection '{selected_collection}'.")


def _add_files_to_collection(collection_name: str, files):
    ids = []
    chunks_all = []
    for file in files:
        text = extract_text_from_pdf(file)
        chunks = chunk_text(text)
        chunks_all.extend(chunks)
        ids.extend([f"{file.name}_{i}" for i in range(len(chunks))])
    add_texts(collection_name, chunks_all, ids)
    st.success(f"Added {len(files)} PDF files to collection '{collection_name}'.")


def _list_files_in_collection(collection_name: str):
    from app.services.chroma_store import get_or_create_collection

    collection = get_or_create_collection(collection_name)
    all_ids = collection.get()["ids"]
    return list(set([i.split("_")[0] for i in all_ids]))


def _delete_files_from_collection(collection_name: str, file_names):
    from app.services.chroma_store import get_or_create_collection

    collection = get_or_create_collection(collection_name)
    for file_name in file_names:
        chunk_ids = [i for i in collection.get()["ids"] if i.startswith(f"{file_name}_")]
        if chunk_ids:
            collection.delete(ids=chunk_ids)
            st.success(f"Deleted file '{file_name}' from collection '{collection_name}'.")
        else:
            st.warning(f"No chunks found for file '{file_name}' in collection '{collection_name}'.")


def chatbot_interface_ui():
    st.header("AI Chatbot Interface")
    from app.services.chroma_store import get_client

    client = get_client()
    collections = [c.name for c in client.list_collections()]

    selected_collection = st.selectbox("Select a Collection", collections)

    if selected_collection:
        st.write(f"Using collection: {selected_collection}")
        chatbot = AIChatbot(selected_collection)

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(_fix_markdown_spacing(message["content"]))

        user_input = st.chat_input("Type your message here...")

        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state["messages"].append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in chatbot.generate_response(user_input):
                    if response.choices[0].delta.content is not None:
                        full_response += response.choices[0].delta.content
                        message_placeholder.markdown(_fix_markdown_spacing(full_response) + "▌")
                cleaned = _fix_markdown_spacing(full_response)
                message_placeholder.markdown(cleaned)
            st.session_state["messages"].append({"role": "assistant", "content": cleaned})
