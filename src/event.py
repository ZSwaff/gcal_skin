import re
from enum import Enum

from src.util import parse_to_utc, to_camel_case


ONE_ON_ONE_REGEX = r'^ *([A-Za-z ]) ?([<>-~]+|:+|/+|\|+|\\+) ?([A-Za-z ]).*$'


class Event:
    class Acceptance(Enum):
        UNKNOWN = 0
        NONE = 1
        MAYBE = 2
        ACCEPTED = 3

    SERIALIZED_ATTRIBUTES = [
        'title',
        'start_dt_str',
        'end_dt_str',
        'location',
        'organizer',
        'is_one_on_one',
        'needs_location',
        'user_acceptance',
        'user_is_organizer',
        'user_has_conflict'
    ]

    def __init__(self, title, start_dt, end_dt, location, organizer_email, attendee_emails, user_email=None, user_acceptance=Acceptance.UNKNOWN):
        self._title = title
        self._start_dt = start_dt
        self._end_dt = end_dt
        self._location = location
        self._organizer_email = organizer_email
        self._attendee_emails = attendee_emails
        self._user_email = user_email
        self._user_acceptance = user_acceptance

        self._user_has_conflict = False

    @property
    def title(self):
        return self._title

    @property
    def start_dt(self):
        return self._start_dt

    @property
    def end_dt(self):
        return self._end_dt

    @property
    def location(self):
        return self._location

    @property
    def organizer_email(self):
        return self._organizer_email

    @property
    def attendee_emails(self):
        return self._attendee_emails

    @property
    def user_email(self):
        return self._user_email

    @property
    def user_acceptance(self):
        return self._user_acceptance

    @property
    def is_one_on_one(self):
        return re.match(ONE_ON_ONE_REGEX, self.title) is not None and len(self.attendee_emails) == 2

    @property
    def needs_location(self):
        return self.location is None

    @property
    def user_is_organizer(self):
        return self.user_email == self.organizer_email

    @property
    def user_has_conflict(self):
        return self._user_has_conflict

    @user_has_conflict.setter
    def user_has_conflict(self, user_has_conflict):
        self._user_has_conflict = user_has_conflict

    def serialize(self):
        return {
            to_camel_case(e): getattr(self, e)
            for e in Event.SERIALIZED_ATTRIBUTES
        }


def from_gcal_event(gcal_event, user_email):
    user_acceptance = Event.Acceptance.UNKNOWN  # todo fix
    attendee_emails = []  # todo fix
    return Event(
        gcal_event['summary'],
        parse_to_utc(gcal_event['start']['dateTime']),
        parse_to_utc(gcal_event['start']['dateTime']),
        gcal_event['location'],
        gcal_event['organizer']['email'],
        attendee_emails,
        user_email,
        user_acceptance
    )

def from_gcal_events(gcal_events, user_email):
    res = [from_gcal_event(e, user_email) for e in gcal_events]
    res.sort(key=lambda x: x.start_dt)
    for i, event in enumerate(res):
        user_has_conflict = False
        for j in range(i - 1, -1, -1):
            pass
            # todo check for conflict and break if so
            # todo break if out of range
        for j in range(i + 1, len(res)):
            pass
            # todo check for conflict and break if so
            # todo break if out of range
        event.user_has_conflict = user_has_conflict
    return res
