# pages/1_👁️_Visualisation.py

import streamlit as st
from utils import get_all_existing_ranges, BASE_DIR

st.set_page_config(page_title="Range Visualisation", page_icon="👁️", layout="wide")

st.title("👁️ Visualisation des Ranges")

# --- DATA LOADING ---
ALL_RANGES = get_all_existing_ranges()

if not ALL_RANGES:
    st.error(
        f"The directory '{BASE_DIR}' is not found, empty, or poorly structured. "
        f"Please ensure it follows the structure: `ranges/depth/position/action.png`"
    )
    st.stop()


# --- PAGE LAYOUT ---
col_img, col_controls = st.columns([2, 1])

with col_controls:
    st.subheader("Select a range")

    depth_list = sorted(ALL_RANGES.keys())
    depth = st.selectbox("Profondeur", depth_list, key="view_depth")

    # The position selectbox depends on the chosen depth
    positions_list = sorted(ALL_RANGES[depth].keys())
    pos = st.selectbox("Position", positions_list, key="view_pos")

    # The action selectbox depends on the depth and position
    actions_list = sorted(ALL_RANGES[depth][pos])
    action = st.selectbox("Action / Sizing", actions_list, key="view_action")

with col_img:
    image_path = BASE_DIR / depth / pos / f"{action}.png"
    if image_path.is_file():
        st.image(str(image_path), use_container_width=False)
    else:
        st.error("Image not found.")
