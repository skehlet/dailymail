import re

def is_google_alert(title):
    return title and title.startswith("Google Alert")

def get_topic_from_google_alert_title(title):
    # Subject: Fwd: Google Alert - "Doors of Stone" release date
    matches = re.search(r'Google Alert - (.+)', title)
    if matches is not None:
        topic = matches.group(1)
        return topic
    return None
