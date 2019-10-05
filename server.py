#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A Flask server for the Google Calendar skin."""


import logging
import json
from datetime import datetime, timedelta

from flask import Flask, jsonify

from src.gcal.client import GcalClient


API_MAJOR_VERSION = '0'

USER_LIST_PATH = './users.json'


def build_default_app():
    with open(USER_LIST_PATH) as fin:
        users = json.load(fin)['users']

    gcal_client = GcalClient()

    return build_app(users, gcal_client)


def build_app(users, cal_client):
    app = Flask(__name__)

    @app.route(f'/api/v{API_MAJOR_VERSION}/users', methods=['GET'])
    def get_user_list():
        return jsonify({
            'users': [
                {
                    'name': e['name'],
                    'email': e['email']
                }
                for e in users
            ]
        })

    @app.route(f'/api/v{API_MAJOR_VERSION}/user/<email>/upcoming-events', methods=['GET'])
    def get_upcoming_events(email):
        start_dt = datetime.utcnow()
        end_dt = start_dt + timedelta(days=1)
        events = cal_client.get_events(email, start_dt, end_dt)
        return jsonify({'events': [e.serialize() for e in events]})

    return app


if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app = build_default_app()
    app.run(host='0.0.0.0', port=5000)
