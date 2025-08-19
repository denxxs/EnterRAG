from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu


def render_top_nav() -> str:
    """Render the top Info/About horizontal menu and return the selected item."""
    return option_menu(
        menu_title=None,
        options=["Info", "About"],
        icons=["bi bi-info-square", "bi bi-globe"],
        orientation="horizontal",
    )


def apply_global_styles():
    st.markdown(
        """
        <style>
        .stButton>button { width: 100%; background-color: #0E1117; border: none; color: white; padding: 12px 20px; text-align: center; font-size: 14px; margin: 4px 0; cursor: pointer; border-radius: 10px; transition-duration: 0.2s; }
        .stButton>button:hover { background-color: #FF4B4B; color : black }
        </style>
        """,
        unsafe_allow_html=True,
    )
