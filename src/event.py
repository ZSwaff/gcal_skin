from src.util import parse_to_utc, to_camel_case


class Event:
    # todo add acceptance status enum (none, accepted, maybe, no response)

    SERIALIZED_ATTRIBUTES = [
        'title',
        'start_dt_str',
        'end_dt_str',
        'location',
        'organizer',
        'is_one_on_one',
        'needs_location',
        'user_acceptance',
        'user_has_conflict',
        'user_is_organizer'
    ]

    def __init__(self, title, start_dt, end_dt, location, organizer, user_acceptance=None):
        self.title = title
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.location = location
        self.organizer = organizer
        self.user_acceptance = user_acceptance

        self.is_one_on_one = None
        self.needs_location = None

        self.user_has_conflict = None
        self.user_is_organizer = None

    # todo add getters/setters as needed

    def serialize(self):
        return {
            to_camel_case(e): getattr(self, e)
            for e in Event.SERIALIZED_ATTRIBUTES
        }


def from_gcal_events(gcal_event):
    return Event(
        gcal_event['summary'],
        parse_to_utc(gcal_event['start']['dateTime']),
        parse_to_utc(gcal_event['start']['dateTime']),
        gcal_event['location'],
        gcal_event['organizer']['email']
    )

def from_gcal_events(user, gcal_events):
    res = [from_gcal_events(e) for e in gcal_events]
    # todo update other attributes based on user
    return res
