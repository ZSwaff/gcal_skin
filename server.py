#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A Flask server for the GCal skin."""


import logging
import json

from flask import Flask, jsonify

from src.gcal_client import GcalClient


API_VERSION = '0.0.1'

USER_LIST_PATH = './users.json'


def build_default_app():
    with open(USER_LIST_PATH) as fin:
        users = json.load(fin)['users']

    gcal_client = GcalClient()

    return build_app(users, gcal_client)


def build_app(users, cal_client):
    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        """Returns the health of the endpoint.
        Returns:
            (str): The string 'OK'.
        """
        return 'OK'

    @app.route(f'/api/{API_VERSION}/users', methods=['GET'])
    def get_user_list():
        return jsonify(users)

    @app.route(f'/api/{API_VERSION}/user/<username>/upcoming-events', methods=['GET'])
    def get_upcoming_events(username):
        return cal_client.get_upcoming_events(username)

    return app


if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app = build_default_app()
    app.run(host='0.0.0.0', port=5000)
