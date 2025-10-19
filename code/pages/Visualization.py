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

POSITION_ORDER = ["LJ", "HJ", "CO", "BTN", "SB", "BB"]
# --- PAGE LAYOUT ---
col_img, col_controls = st.columns([2, 1])

with col_controls:
    st.subheader("Select a range")

    depth_list = sorted(
        ALL_RANGES.keys(), key=lambda x: int(x.split("bb")[0]), reverse=True
    )
    # Changed selectbox to radio
    depth = st.radio("Profondeur", depth_list, key="view_depth", horizontal=True)

    positions_list = [pos for pos in POSITION_ORDER if pos in POSITION_ORDER]

    # Fallback: if any available positions are NOT in the custom order,
    # add them to the end, sorted alphabetically.
    # This makes the code more robust if you add new positions later.
    other_positions = sorted(
        [pos for pos in POSITION_ORDER if pos not in POSITION_ORDER]
    )
    positions_list.extend(other_positions)
    pos = st.radio("Position", positions_list, key="view_pos", horizontal=True)

    # The action radio buttons depend on the depth and position
    actions_list = sorted(ALL_RANGES[depth][pos])
    # Changed selectbox to radio
    action = st.radio(
        "Action / Sizing",
        actions_list,
        key="view_action",
        horizontal=True,
        index=len(actions_list) - 1,
    )

with col_img:
    image_path = BASE_DIR / depth / pos / f"{action}.png"
    if image_path.is_file():
        st.image(str(image_path), use_container_width=False)
    else:
        st.error("Image not found.")
