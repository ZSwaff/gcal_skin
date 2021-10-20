import csv
import json
import sys
import os

from datetime import datetime, timedelta
from pytz import timezone

import pandas as pd

from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import HoverTool

sys.path.append(os.path.abspath('../src'))
from util import parse_dt_to_utc
from gcal.util import get_client
from event import from_gcal_events


USERNAME = 'zdfs1121@gmail.com'
START_DT = datetime(2018, 1, 1)
END_DT = datetime(2021, 10, 18)
LOCAL_TZ = timezone('America/Los_Angeles')

START_DT_STR = START_DT.isoformat() + 'Z'
END_DT_STR = END_DT.isoformat() + 'Z'


CACHE_PATH = 'PERSONAL_EVENT_CACHE.csv'


# load events from cache or from gcal
def load_events():
    if not os.path.exists(CACHE_PATH):
        calendar = get_client()

        all_results = []
        req = calendar.events().list(
            calendarId=USERNAME,
            timeMin=START_DT_STR,
            timeMax=END_DT_STR,
            singleEvents=True,
            orderBy='startTime'
        )
        while req:
            res = req.execute()
            all_results += res['items']
            req = calendar.events().list_next(req, res)
            print(all_results[-1].get('start', {}).get('dateTime'))

        headers = set()
        for e in all_results:
            headers |= e.keys()

        with open(CACHE_PATH, 'w+') as fout:
            writer = csv.DictWriter(fout, fieldnames=list(headers))
            writer.writeheader()
            for e in all_results:
                writer.writerow(e)

    return pd.read_csv(CACHE_PATH)


gcal_events = load_events()

print('Days:', (END_DT - START_DT).days)
print('Evts:', len(gcal_events))
print('Cols:', gcal_events.columns)


# transform gcal events to nice event models, and those to dataframe
event_models = from_gcal_events(gcal_events, USERNAME)
events = pd.DataFrame([e.serialize() for e in event_models])


def extract_dt_props(row):
    sdl = parse_dt_to_utc(row.startDtStr).astimezone(LOCAL_TZ)
    edl = parse_dt_to_utc(row.endDtStr).astimezone(LOCAL_TZ)
    day_of_week = int(sdl.strftime('%w'))
    month_start = datetime.strptime(sdl.strftime('%Y-%m-01'), '%Y-%m-%d')
    week_start = datetime.strptime(sdl.strftime('%Y-%m-%d'), '%Y-%m-%d') - timedelta(days=day_of_week)
    return {
        'year': sdl.strftime('%Y'),
        'yearMonth': sdl.strftime('%Y-%m'),
        'monthOfYear': sdl.strftime('%m'),
        'monthStartDt': month_start,
        'monthStart': month_start.strftime('%Y-%m-%d'),
        'date': sdl.strftime('%Y-%m-%d'),
        'dayOfWeek': day_of_week,
        'yearWeek': sdl.strftime('%Y~%U'),
        'weekStartDt': week_start,
        'weekStart': week_start.strftime('%Y-%m-%d'),
        'weekOfYear': sdl.strftime('%U'),
        'durationSec': (edl - sdl).total_seconds()
    }


events = events.join(pd.DataFrame(extract_dt_props(e) for _, e in events.iterrows()))
events = events[events.durationSec < 604800]
events.head()

months = events.groupby(['monthStartDt', 'monthStart']).agg(meetingCount=('title', 'count'), totalSec=('durationSec', 'sum')).reset_index()
months['totalHr'] = months.totalSec / 3600
weeks = events.groupby(['weekStartDt', 'weekStart']).agg(meetingCount=('title', 'count'), totalSec=('durationSec', 'sum')).reset_index()
weeks['totalHr'] = weeks.totalSec / 3600
weeks.head()

hover = HoverTool(tooltips=[
    ('Week', '@weekStart'),
    ('Hours in Meetings', '@totalHr'),
    ('Number of Meetings', '@meetingCount')
])
plot = figure(title='Hours Spent in Meetings by Week', x_axis_type='datetime', tools=[hover], plot_width=1600, plot_height=800)
plot.toolbar_location = None
plot.toolbar.active_drag = None
plot.toolbar.active_scroll = None
plot.toolbar.active_tap = None
plot.line(x='weekStartDt', y='totalHr', source=weeks, line_width=2)
show(plot)

# p = figure(title='Hours Spent in Meetings by Month', x_axis_type='datetime', plot_width=1600, plot_height=800)
# p.line(x='monthStartDt', y='totalHr', source=months, line_width=2)
# show(p)
