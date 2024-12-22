import streamlit as st
from utils.page_utils import initialize_session_state, render_class_inputs, fetch_and_filter_classes
from utils.calendar_utils import create_calendar, convert_days
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
BASE_API_URL = os.getenv("API_BASE_URL")
QUARTER_START = datetime.strptime(os.getenv("FDI"), "%d/%m/%Y")
QUARTER_END = datetime.strptime(os.getenv("LDI"), "%d/%m/%Y")

# Custom CSS to match the React design
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Card styling */
    .stCard {
        padding: 1rem;
        border-radius: 8px;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Step boxes styling */
    .step-box {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .step-number {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Button styling */
    .stButton button {
        width: 100%;
    }
    
    /* Help section styling */
    .help-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    @media (max-width: 768px) {
        .stColumn {
            margin-bottom: 1rem !important;  /* Force override any existing margins */
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; font-size: 2rem; margin-bottom: 0.5rem;'>UCSD Class Fetcher</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Generate your class schedule calendar in just a few clicks</p>", unsafe_allow_html=True)

# Steps section using columns
# Add container with bottom margin
st.markdown("<div style='margin-bottom: 2rem;'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #f0f7ff; border-radius: 8px;'>
            <div style='font-size: 2rem; color: #2563eb; font-weight: bold;'>1</div>
            <h3 style='margin: 0.5rem 0; color: #1e293b;'>Add Classes</h3>
            <p style='font-size: 0.9rem; color: #475569;'>Enter your course codes and section numbers</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #f0fdf4; border-radius: 8px;'>
            <div style='font-size: 2rem; color: #16a34a; font-weight: bold;'>2</div>
            <h3 style='margin: 0.5rem 0; color: #1e293b;'>Fetch Info</h3>
            <p style='font-size: 0.9rem; color: #475569;'>Retrieve your class details and schedules</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #faf5ff; border-radius: 8px;'>
            <div style='font-size: 2rem; color: #9333ea; font-weight: bold;'>3</div>
            <h3 style='margin: 0.5rem 0; color: #1e293b;'>Get Calendar</h3>
            <p style='font-size: 0.9rem; color: #475569;'>Download your schedule as an iCal file</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # Close the container

# Help section with expander
with st.expander("Need Help?"):
    st.markdown("""
        ### 📝 Adding Classes
        Use the input fields to enter course codes and section numbers. Click "Add Class" for more fields or "Remove Class" to delete them.
        
        ### 🔍 Fetching Information
        Click "Fetch Classes" to retrieve details. The information will appear below the input fields.
        
        ### 📅 Calendar Generation
        After fetching classes, click "Generate Calendar" then "Download Calendar" to save your schedule.
        
        ### 🔄 Starting Over
        Use "Clear All" to reset all fields and start fresh.
    """)

# Initialize session state
initialize_session_state("input_fields", [(None, None)])
initialize_session_state("classes", [])

# Render input fields
st.session_state.input_fields = render_class_inputs()

# Add/Remove Class buttons
cols = st.columns(2)
with cols[0]:
    if st.button("➕Add Class", use_container_width=True):
        st.session_state.input_fields.append((None, None))
        st.rerun()

with cols[1]:
    if st.button("➖Remove Class", use_container_width=True) and len(st.session_state.input_fields) > 1:
        st.session_state.input_fields.pop()
        st.rerun()

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍Fetch Classes", use_container_width=True):
        classes = fetch_and_filter_classes(
            st.session_state.input_fields, BASE_API_URL)
        st.session_state.classes = classes
        st.rerun()

with col2:
    if st.session_state.classes and st.button("📅Generate Calendar", use_container_width=True):
        calendar_content = create_calendar(
            st.session_state.classes,
            QUARTER_START.strftime('%Y-%m-%d'),
            QUARTER_END.strftime('%Y-%m-%d')
        )
        if calendar_content:
            st.download_button(
                label="🔽Download Calendar",
                data=calendar_content,
                file_name="class_schedule.ics",
                mime="text/calendar",
                key="download_calendar",
                use_container_width=True
            )

with col3:
    if st.button("🔁Clear All", use_container_width=True):
        st.session_state.input_fields = [(None, None)]
        st.session_state.classes = []
        st.rerun()


# Helper function to format days
def format_days(days_str: str) -> str:
    """Convert abbreviated days to full day names and format them nicely"""
    full_days = convert_days(days_str)
    return " and ".join(full_days) if len(full_days) == 2 else ", ".join(full_days)


# Display fetched classes
if st.session_state.classes:
    st.subheader("Fetched Classes")
    for class_code, info in st.session_state.classes.items():
        with st.expander(f"📚 {class_code}"):
            st.markdown("**Lecture:**")
            st.write(f"Days: {format_days(info['lecture_info']['days'])}")
            st.write(f"Time: {info['lecture_info']['time']}")
            st.write(f"Location: {info['lecture_info']['location']}")

            if "discussion_info" in info:
                st.markdown("\n**Discussion:**")
                st.write(f"Days: {format_days(
                    info['discussion_info']['days'])}")
                st.write(f"Time: {info['discussion_info']['time']}")
                st.write(f"Location: {info['discussion_info']['location']}")
            else:
                st.write("No discussion section available.")
