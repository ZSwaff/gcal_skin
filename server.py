#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A Flask server for the GCal skin."""


import logging
import json

from flask import Flask, request, jsonify


API_VERSION = '0.0.1'

USER_LIST_PATH = './users.json'


def build_default_app():
    with open(USER_LIST_PATH) as fin:
        users = json.load(fin)['users']

    return build_app(users)


def build_app(users):
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

    return app


if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app = build_default_app()
    app.run(host='0.0.0.0', port=5000)
