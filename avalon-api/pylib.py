"""This functions are used is the RESTful web service of Avalon"""

import rethinkdb as r
from flask import Blueprint, jsonify, make_response, request, send_file
from flask_cors import CORS

from avalon.db_utils import db_connect, db_get_game, db_get_table, db_get_value, resolve_key_id, restart_db
from avalon.exception import AvalonError
from avalon.games import game_put, game_guess_merlin
from avalon.mp3 import get_mp3_roles_path
from avalon.rules import get_rules

from api_utils import HTTPError


AVALON_BLUEPRINT = Blueprint("avalon", __name__)
CORS(AVALON_BLUEPRINT)

AVALON_BLUEPRINT.before_request(db_connect)


# from flask_httpauth import HTTPBasicAuth
# from werkzeug.security import generate_password_hash, check_password_hash

# AUTH = HTTPBasicAuth()

# USERS = {
#     "mathieu": generate_password_hash("lebeaugosse"),
#     "romain": generate_password_hash("lala")
# }


# @AUTH.verify_password
# def verify_password(username, password):
#     if username in USERS:
#         return check_password_hash(USERS.get(username), password)
#     return False


# @AVALON_BLUEPRINT.route('/')
# @AUTH.login_required
# def index():
#     return "Hello, %s!" % AUTH.username()


@AVALON_BLUEPRINT.route("/restart_db", methods=["PUT"])
#@AUTH.login_required
def put_restart_db():
    """
    This function deletes all tables in the post request and initializes them.
        - method: PUT
        - route: /restart_db
        - payload example: [
                               "games",
                               "players"
                               "quests",
                               "users"
                           ]
    """
    try:
        response_msg = restart_db(payload_tables=request.json)
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return make_response(response_msg, 204)


@AVALON_BLUEPRINT.route('/games/<string:game_id>/mp3', methods=['GET'])
def get_mp3(game_id):
    """This function creates the mp3file depending on roles of players.
        - method: GET
        - route: /<game_id>/mp3
        - payload example:
        - response example: response.mpga
    """
    try:
        mp3_roles_path = get_mp3_roles_path(game_id=game_id)
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return send_file(mp3_roles_path, attachment_filename="roles.mp3", mimetype="audio/mpeg")


@AVALON_BLUEPRINT.route('/rules', methods=['GET'])
def get_rules_conf():
    """
    This function visualizes a table depending on the input <table_name>.
        - method: GET
        - route: /<table_name> (table_name is games and players)
    """
    try:
        rules = get_rules()
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return jsonify(rules)


@AVALON_BLUEPRINT.route('/players', methods=['GET'])
def get_players():
    """
    This function visualizes a table depending on the input <table_name>.
        - method: GET
        - route: /<table_name> (table_name is games and players)
    """
    try:
        table_players = db_get_table(table_name="players")
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return jsonify(table_players)


@AVALON_BLUEPRINT.route('/games/<string:game_id>/guess_merlin', methods=['POST'])
def guess_merlin(game_id):
    """
    """
    try:
        updated_game = game_guess_merlin(game_id=game_id, payload=request.json)
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return jsonify(updated_game)


@AVALON_BLUEPRINT.route('/quests', methods=['GET'])
def get_quests():
    """
    This function visualizes a table depending on the input <table_name>.
        - method: GET
        - route: /<table_name> (table_name is games and players)
    """
    try:
        table_quests = db_get_table(table_name="quests")
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return jsonify(table_quests)


@AVALON_BLUEPRINT.route("/games/<string:game_id>", methods=["GET", "PUT"])
@AVALON_BLUEPRINT.route("/games", methods=["GET", "PUT"])
def games(game_id=None):

    if request.method == "GET":
        try:
            game = db_get_game(game_id=game_id)
        except AvalonError as error:
            raise HTTPError(str(error), status_code=400) from error

    if request.method == "PUT":
        try:
            game = game_put(payload=request.json)
        except AvalonError as error:
            raise HTTPError(str(error), status_code=400) from error

    return jsonify(game)
