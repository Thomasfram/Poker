# 🏠_Home.py

import streamlit as st
from utils import get_all_existing_ranges, BASE_DIR

# --- PAGE CONFIGURATION ---
# This should be the first Streamlit command in your app, and it's only run once.
st.set_page_config(page_title="Poker Range Trainer", page_icon="♠️", layout="wide")


# --- MAIN PAGE CONTENT ---

st.title("♠️ Welcome to the Poker Range Trainer!")
st.sidebar.success("Select a mode above.")

st.markdown(
    """
    This application is designed to help you study and memorize poker ranges.
    
    **👈 Select a mode from the sidebar to get started:**

    - **👁️ Visualisation**: Browse and view all your saved poker ranges.
    - **🧠 Quiz**: Test your knowledge by guessing the correct situation for a given range.

    ### Setup
    Please make sure your ranges are organized in the following folder structure:
    """
)

st.code("ranges/depth/position/action.png", language="bash")
st.info(
    f"The app is currently looking for ranges in the `{BASE_DIR}` directory.", icon="📁"
)

# You can optionally display a summary of loaded ranges here
ALL_RANGES = get_all_existing_ranges()
if not ALL_RANGES:
    st.error(
        f"The directory '{BASE_DIR}' was not found or is empty. "
        "Please check your setup.",
        icon="🚨",
    )
else:
    st.success(
        f"Successfully loaded {sum(len(pos) for depth in ALL_RANGES.values() for pos in depth.values())} "
        "ranges from the directory.",
        icon="✅",
    )
