from src.gcal.util import get_client
from src.event import from_gcal_events


class GcalClient:
    def __init__(self):
        self.calendar = get_client()

    def get_events(self, email, start_dt, end_dt):
        results = []
        req = self.calendar.events().list(
            calendarId=email,
            timeMin=start_dt.isoformat() + 'Z',
            timeMax=end_dt.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        )
        while req:
            res = req.execute()
            results += res['items']
            req = self.calendar.events().list_next(req, res)
        return from_gcal_events(results, email)
