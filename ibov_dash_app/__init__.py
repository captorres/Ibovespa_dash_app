from flask import Flask

app = Flask(__name__)

from ibov_dash_app import routes
