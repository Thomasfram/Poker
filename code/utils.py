# utils.py

import streamlit as st
import random
from pathlib import Path

# --- CONSTANTS ---
BASE_DIR = Path("ranges")


# --- UTILITY FUNCTIONS ---


@st.cache_data
def get_all_existing_ranges():
    """
    Scans the directory structure once and returns a structured dictionary
    of all valid combinations (depth > position > actions).
    Example return:
    {
        '100bb': {
            'BTNvsBB': ['RFI', '3bet'],
            'LJvsCO': ['4bet']
        },
        '20bb': { ... }
    }
    """
    structured_ranges = {}
    if not BASE_DIR.is_dir():
        return structured_ranges

    for depth_path in BASE_DIR.iterdir():
        if depth_path.is_dir():
            depth = depth_path.name
            structured_ranges[depth] = {}
            for pos_path in depth_path.iterdir():
                if pos_path.is_dir():
                    pos = pos_path.name
                    actions = [f.stem for f in pos_path.glob("*.png")]
                    if actions:
                        structured_ranges[depth][pos] = sorted(actions)

    # Filter out any empty depths or positions
    structured_ranges = {d: p for d, p in structured_ranges.items() if p}
    return structured_ranges


def get_random_range_from_structure(all_ranges):
    """
    Chooses a random range from the structured dictionary.
    """
    if not all_ranges:
        return None, None

    # Pick a valid depth, then position, then action
    random_depth = random.choice(list(all_ranges.keys()))
    random_pos = random.choice(list(all_ranges[random_depth].keys()))
    random_action = random.choice(all_ranges[random_depth][random_pos])

    image_path = BASE_DIR / random_depth / random_pos / f"{random_action}.png"

    correct_answer = {"depth": random_depth, "pos": random_pos, "action": random_action}

    return str(image_path), correct_answer
