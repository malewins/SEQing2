# import abc
from flask import Flask
from dash_auth import BasicAuth
import dash

# THIS IS JUST FOR TEST PURPOSE. Keep this out of source code repository
VALID_USERNAME_PASSWORD_PAIRS = {
    'user': 'test'
}

server = Flask(__name__)
app = dash.Dash(server=server)
auth = BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

"""class AppInterface:
    Interface to handel multiple callbacks in different classes.

    def __init__(self, app=None):
        self.server = Flask(__name__)
        self.app = dash.Dash(server=self.server)

        if self.app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.app)
"""
