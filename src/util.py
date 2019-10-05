from datetime import datetime

from pytz import timezone


UTC = timezone('UTC')
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def parse_to_utc(dt):
    return UTC.localize(datetime.strptime(dt, ISO_FORMAT)).replace(tzinfo=None)

def to_camel_case(s):
    frags = s.split('_')
    return frags[0] + ''.join(e.title() for e in frags[1:])
