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


def get_rrule_days(days: List[str]) -> str:
    """
    Convert full day names to RRULE day format.

    Args:
        days (List[str]): List of full day names

    Returns:
        str: RRULE-formatted day string
    """
    rrule_mapping = {
        'Monday': 'MO',
        'Tuesday': 'TU',
        'Wednesday': 'WE',
        'Thursday': 'TH',
        'Friday': 'FR',
        'Saturday': 'SA',
        'Sunday': 'SU'
    }
    return ','.join(rrule_mapping[day] for day in days)


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
        List[Dict]: List of recurring events for all classes
    """
    all_events = []
    start_date = datetime.strptime(term_start, '%Y-%m-%d')
    end_date = datetime.strptime(term_end, '%Y-%m-%d')

    # Process each class
    for class_code, sessions in class_data.items():
        # Process lecture and discussion sessions
        for session_type in ['lecture_info', 'discussion_info']:
            if session_type in sessions:
                session = sessions[session_type]
                class_days = convert_days(session['days'])
                rrule_days = get_rrule_days(class_days)

                # Find first occurrence of the class
                first_date = start_date
                while first_date <= end_date:
                    if first_date.strftime('%A') in class_days:
                        break
                    first_date += timedelta(days=1)

                start_time = datetime.strptime(
                    session['startTime'], '%H:%M').time()
                end_time = datetime.strptime(
                    session['endTime'], '%H:%M').time()

                event = {
                    'title': f"{class_code} {session_type.split('_')[0].title()}",
                    'date': first_date.strftime('%Y-%m-%d'),
                    'start_time': start_time.strftime('%H:%M'),
                    'end_time': end_time.strftime('%H:%M'),
                    'location': session['location'],
                    'section': session['section'],
                    'rrule': {
                        'freq': 'WEEKLY',
                        'until': end_date.strftime('%Y%m%d'),
                        'byday': rrule_days
                    }
                }
                all_events.append(event)

    return all_events


def generate_ics_content(events: List[Dict]) -> str:
    """
    Generate ICS file content from events with recurring rules.

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

        rrule = event['rrule']
        rrule_str = f"FREQ={rrule['freq']};UNTIL={
            rrule['until']}T235959Z;BYDAY={rrule['byday']}"

        ics_content.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid4()}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start_datetime.replace('-', '').replace(':', '')}",
            f"DTEND:{end_datetime.replace('-', '').replace(':', '')}",
            f"RRULE:{rrule_str}",
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
