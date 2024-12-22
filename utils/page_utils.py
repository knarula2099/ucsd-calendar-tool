import streamlit as st
import requests


def initialize_session_state(key, default_value):
    """
    Initialize a session state key with a default value if not already set.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value


def render_class_inputs():
    updated_inputs = []
    for i, (course_code, section_id) in enumerate(st.session_state.input_fields):
        cols = st.columns(2)
        updated_inputs.append((
            cols[0].text_input(f"Enter Course Code {
                               i + 1}", value=course_code or "", key=f"course_{i}", placeholder="eg. CSE 101, MATH 20C, Econ 138"),
            cols[1].text_input(f"Enter Section ID {
                               i + 1}", value=section_id or "", key=f"section_{i}", placeholder="eg. A01, B02. Use Lecture ID if no discussion section.")
        ))
    return updated_inputs


def fetch_and_filter_classes(input_fields, base_url):
    """
    Fetch details for valid classes from the API and filter based on section ID.

    Args:
        input_fields (list): List of tuples containing (course_code, section_id).
        base_url (str): Base URL of the API.

    Returns:
        dict: Filtered class information with lecture and discussion details for each class.
    """
    valid_classes = [
        (course_code, section_id)
        for course_code, section_id in input_fields
        if course_code and section_id
    ]

    if not valid_classes:
        st.error(
            "No valid classes entered. Please add valid Course Code and Section ID.")
        return {}

    filtered_class_info = {}

    for course_code, section_id in valid_classes:
        response = requests.get(f"{base_url}/{course_code}")
        if response.status_code == 200:
            data = response.json()
            section_id = section_id.upper()
            course_code = course_code.upper().replace(" ", "")
            class_key = f"{course_code}_{section_id}"

            lecture_section = section_id[:-1] + '0'

            # Extract relevant lecture and discussion info
            lecture_info = next(
                (lecture for lecture in data.get("lecture_info", [])
                 if lecture["section"] == lecture_section), None
            )
            discussion_info = next(
                (discussion for discussion in data.get("discussion_info", [])
                 if discussion["section"] == section_id), None
            )

            if lecture_info and discussion_info:
                filtered_class_info[class_key] = {
                    "lecture_info": lecture_info,
                    "discussion_info": discussion_info,
                }
            elif lecture_info:
                filtered_class_info[class_key] = {
                    "lecture_info": lecture_info,
                }
            else:
                st.warning(f"Lecture or discussion info not found for {
                           course_code} - {section_id}.")
        else:
            st.error(f"Failed to fetch details for {
                     course_code} - {section_id}")

    return filtered_class_info
