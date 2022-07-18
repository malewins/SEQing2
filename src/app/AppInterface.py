# import abc
from flask import Flask
import dash


# THIS IS JUST FOR TEST PURPOSE. Keep this out of source code repository


server = Flask(__name__)
app = dash.Dash(server=server)
#auth = BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
