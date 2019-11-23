from datetime import datetime, timezone


ISO_DATE_FORMAT = '%Y-%m-%d'
ISO_DT_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def parse_date_to_utc(dt_str):
    return datetime.strptime(dt_str, ISO_DATE_FORMAT).astimezone(tz=timezone.utc)

def parse_dt_to_utc(dt_str):
    return datetime.strptime(dt_str, ISO_DT_FORMAT).astimezone(tz=timezone.utc)

def print_dt_to_utc(dt):
    return dt.isoformat() + 'Z'

def to_camel_case(s):
    frags = s.split('_')
    return frags[0] + ''.join(e.title() for e in frags[1:])
