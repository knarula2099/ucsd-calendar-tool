import streamlit as st
from utils.page_utils import initialize_session_state, render_class_inputs, fetch_and_filter_classes
from utils.calendar_utils import create_calendar, convert_days
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
BASE_API_URL = os.getenv("API_BASE_URL")
# First Day of Instruction
QUARTER_START = datetime.strptime(os.getenv("FDI"), "%d/%m/%Y")
# Last Day of Instruction
QUARTER_END = datetime.strptime(os.getenv("LDI"), "%d/%m/%Y")

st.header("UCSD Class Fetcher")

# Initialize session state for input fields
initialize_session_state("input_fields", [(None, None)])
initialize_session_state("classes", [])

# Render input fields
st.session_state.input_fields = render_class_inputs()

# Add/Remove Class buttons
cols = st.columns(2)
with cols[0]:
    if st.button("Add Class", use_container_width=True):
        st.session_state.input_fields.append((None, None))
        st.rerun()

with cols[1]:
    if st.button("Remove Class", use_container_width=True) and len(st.session_state.input_fields) > 1:
        st.session_state.input_fields.pop()
        st.rerun()

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    # Fetch classes information
    if st.button("Fetch Classes", use_container_width=True):
        classes = fetch_and_filter_classes(
            st.session_state.input_fields, BASE_API_URL)
        st.session_state.classes = classes
        st.rerun()

with col2:
    # Generate calendar
    if st.session_state.classes and st.button("Generate Calendar", use_container_width=True):
        calendar_content = create_calendar(
            st.session_state.classes,
            QUARTER_START.strftime('%Y-%m-%d'),
            QUARTER_END.strftime('%Y-%m-%d')
        )
        if calendar_content:
            st.download_button(
                label="Download Calendar",
                data=calendar_content,
                file_name="class_schedule.ics",
                mime="text/calendar",
                key="download_calendar"
            )

with col3:
    # Clear all
    if st.button("Clear All", use_container_width=True):
        st.session_state.input_fields = [(None, None)]
        st.session_state.classes = []
        st.rerun()

# Helper function to format days


def format_days(days_str: str) -> str:
    """Convert abbreviated days to full day names and format them nicely"""
    full_days = convert_days(days_str)
    return " and ".join(full_days) if len(full_days) == 2 else ", ".join(full_days)


# Display fetched classes with full day names
if st.session_state.classes:
    st.subheader("Fetched Classes")
    for class_code, info in st.session_state.classes.items():
        with st.expander(f"📚 {class_code}"):
            # Lecture information
            st.write("**Lecture:**")
            st.write(f"Days: {format_days(info['lecture_info']['days'])}")
            st.write(f"Time: {info['lecture_info']['time']}")
            st.write(f"Location: {info['lecture_info']['location']}")

            if "discussion_info" in info:
                # Discussion information
                st.write("\n**Discussion:**")
                st.write(f"Days: {format_days(
                    info['discussion_info']['days'])}")
                st.write(f"Time: {info['discussion_info']['time']}")
                st.write(f"Location: {info['discussion_info']['location']}")
            else:
                st.write("No discussion section available.")
