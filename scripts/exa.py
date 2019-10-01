import datetime
import json

from src.gcal.util import get_client


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    calendar = get_client()

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = calendar.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    print(json.dumps(events, indent=2))


if __name__ == '__main__':
    main()
