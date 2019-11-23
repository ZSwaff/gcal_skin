import re
from enum import Enum

import pandas as pd

from util import parse_dt_to_utc, parse_date_to_utc, print_dt_to_utc, to_camel_case


ONE_ON_ONE_REGEX = r'^ *([A-Za-z -]) ?([<>-~]+|:+|/+|\|+|\\+) ?([A-Za-z -]).*$'


class Event:
    class Acceptance(Enum):
        UNKNOWN = 0
        NONE = 1
        DECLINED = 2
        MAYBE = 3
        ACCEPTED = 4

    # todo convert to wrapper
    SERIALIZED_ATTRIBUTES = [
        'title',
        'start_dt_str',
        'end_dt_str',
        'location',
        'organizer_email',
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
    def start_dt_str(self):
        return print_dt_to_utc(self._start_dt)

    @property
    def end_dt(self):
        return self._end_dt

    @property
    def end_dt_str(self):
        return print_dt_to_utc(self._end_dt)

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


def acceptance_from_gcal_attendee_response_status(gcal_attendee_response_status):
    return {
        'accepted': Event.Acceptance.ACCEPTED,
        'declined': Event.Acceptance.DECLINED,
        'needsAction': Event.Acceptance.NONE,
        'tentative': Event.Acceptance.MAYBE
    }[gcal_attendee_response_status]

def get_dt_from_gcal_event(gcal_event, dt_key):
    dt = eval(gcal_event[dt_key])
    if 'dateTime' in dt:
        return parse_dt_to_utc(dt['dateTime'])
    else:
        return parse_date_to_utc(dt['date'])

def from_gcal_event(gcal_event, user_email):
    title = gcal_event['summary']
    if pd.isnull(title):
        return None

    raw_attendees = gcal_event['attendees']
    if pd.isnull(raw_attendees):
        return None

    attendees = eval(gcal_event['attendees'])
    user_attendees = [e for e in attendees if e.get('self', False)]
    if len(user_attendees) != 1:
        return None

    user_attendee = user_attendees[0]
    user_acceptance = acceptance_from_gcal_attendee_response_status(user_attendee['responseStatus'])
    attendee_emails = [e['email'] for e in attendees]

    return Event(
        title,
        get_dt_from_gcal_event(gcal_event, 'start'),
        get_dt_from_gcal_event(gcal_event, 'end'),
        gcal_event['location'],
        eval(gcal_event['organizer'])['email'],
        attendee_emails,
        user_email,
        user_acceptance
    )

def from_gcal_events(gcal_events, user_email):
    if isinstance(gcal_events, pd.core.frame.DataFrame):
        gcal_events = gcal_events.to_dict('records')
    raw_events = [from_gcal_event(e, user_email) for e in gcal_events]
    events = [e for e in raw_events if e is not None]

    events.sort(key=lambda x: x.end_dt)
    for i, event in enumerate(events[1:], 1):
        last_event = events[i - 1]
        if event.start_dt < last_event.end_dt:
            event.user_has_conflict = True
            last_event.user_has_conflict = True
    events.sort(key=lambda x: x.start_dt)
    for i, event in enumerate(events[:-1]):
        next_event = events[i + 1]
        if event.end_dt > next_event.start_dt:
            event.user_has_conflict = True
            next_event.user_has_conflict = True

    return events
