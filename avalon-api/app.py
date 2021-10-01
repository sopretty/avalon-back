# -*- coding: utf-8 -*-
# author: romain.121@hotmail.fr

"""This script is the RESTful web service used in Avalon"""

import argparse
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from mp3 import create_mp3
from pylib import AVALON_BLUEPRINT
from quests import QUESTS_BLUEPRINT
from games import GAMES_BLUEPRINT

# from db_utils import db_connect

APP = Flask(__name__)
APP.register_blueprint(AVALON_BLUEPRINT)
APP.register_blueprint(GAMES_BLUEPRINT)
APP.register_blueprint(QUESTS_BLUEPRINT)

# APP.before_first_request(db_connect)


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser()

    # optional arguments
    PARSER.add_argument("-host", type=str, help="app host", default='0.0.0.0')
    PARSER.add_argument("-port", type=int, help="app port", default=5000)
    PARSER.add_argument("-host_db", type=str, help="db host", default='rethinkdb')
    PARSER.add_argument("-port_db", type=int, help="db port", default=28015)

    # parse arguments
    ARGS = PARSER.parse_args()

    HANDLER = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    HANDLER.setLevel(logging.INFO)
    APP.logger.addHandler(HANDLER)

    create_mp3()

    # print(APP.before_first_request_funcs)

    # Start the RESTful web service used in Avalon
    APP.run(host=ARGS.host, port=ARGS.port, debug=True)
