# utils/calendar_utils.py

from datetime import datetime, timedelta
from typing import List, Dict
from uuid import uuid4


def convert_days(day_string: str) -> List[str]:
    """
    Convert abbreviated days to full day names.

    Args:
        day_string (str): String of abbreviated days (e.g., 'TuTh', 'MWF')

    Returns:
        List[str]: List of full day names
    """
    day_mapping = {
        'M': 'Monday',
        'Tu': 'Tuesday',
        'W': 'Wednesday',
        'Th': 'Thursday',
        'F': 'Friday',
        'Sa': 'Saturday',
        'Su': 'Sunday'
    }

    full_days = []
    i = 0
    while i < len(day_string):
        if i + 1 < len(day_string) and day_string[i:i+2] in day_mapping:
            full_days.append(day_mapping[day_string[i:i+2]])
            i += 2
        else:
            full_days.append(day_mapping[day_string[i]])
            i += 1

    return full_days


def create_class_events(
    class_data: Dict,
    term_start: str,
    term_end: str
) -> List[Dict]:
    """
    Create recurring events for all classes based on schedule and date range.

    Args:
        class_data (Dict): Dictionary containing all class information
        term_start (str): Start date in 'YYYY-MM-DD' format
        term_end (str): End date in 'YYYY-MM-DD' format

    Returns:
        List[Dict]: List of all events for all classes
    """
    all_events = []
    start_date = datetime.strptime(term_start, '%Y-%m-%d')
    end_date = datetime.strptime(term_end, '%Y-%m-%d')

    weekday_mapping = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }

    # Process each class
    for class_code, sessions in class_data.items():
        # Process lecture and discussion sessions
        for session_type in ['lecture_info', 'discussion_info']:
            if session_type in sessions:
                session = sessions[session_type]
                class_days = convert_days(session['days'])
                class_weekdays = [weekday_mapping[day] for day in class_days]

                start_time = datetime.strptime(
                    session['startTime'], '%H:%M').time()
                end_time = datetime.strptime(
                    session['endTime'], '%H:%M').time()

                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() in class_weekdays:
                        event = {
                            'title': f"{class_code} {session_type.split('_')[0].title()}",
                            'date': current_date.strftime('%Y-%m-%d'),
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'location': session['location'],
                            'section': session['section']
                        }
                        all_events.append(event)
                    current_date += timedelta(days=1)

    return all_events


def generate_ics_content(events: List[Dict]) -> str:
    """
    Generate ICS file content from events.

    Args:
        events (List[Dict]): List of event dictionaries

    Returns:
        str: ICS file content as a string
    """
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//UCSD//Calendar Constructor//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    for event in events:
        start_datetime = f"{event['date']}T{event['start_time']}:00"
        end_datetime = f"{event['date']}T{event['end_time']}:00"

        ics_content.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid4()}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start_datetime.replace('-', '').replace(':', '')}",
            f"DTEND:{end_datetime.replace('-', '').replace(':', '')}",
            f"SUMMARY:{event['title']}",
            f"LOCATION:{event['location']}",
            f"DESCRIPTION:Section {event['section']}",
            "END:VEVENT"
        ])

    ics_content.append("END:VCALENDAR")
    return '\n'.join(ics_content)


def create_calendar(class_data: Dict, term_start: str, term_end: str) -> str:
    """
    Main function to create calendar file content from class data.

    Args:
        class_data (Dict): Dictionary containing all class information
        term_start (str): Start date in 'YYYY-MM-DD' format
        term_end (str): End date in 'YYYY-MM-DD' format

    Returns:
        str: ICS file content as a string
    """
    # Generate all events
    events = create_class_events(class_data, term_start, term_end)

    # Generate ICS content
    if events:
        return generate_ics_content(events)
    return None
