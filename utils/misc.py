from datetime import datetime

def convert_human_readable_date_time(timestamp_str):
    # Convert the timestamp string to a datetime object
    timestamp = datetime.fromisoformat(str(timestamp_str))  

    # Convert the datetime object to a human-readable format
    human_readable_time = timestamp.strftime("%d-%m-%Y %H:%M:%S")

    return human_readable_time