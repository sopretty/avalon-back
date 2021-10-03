"""This functions are used is the RESTful web service of Avalon"""

import rethinkdb as r
from flask import Blueprint, jsonify, make_response, request, send_file
from flask_cors import CORS

from avalon.db_utils import db_connect, db_get_game, db_get_table, db_get_value, resolve_key_id, restart_db
from avalon.exception import AvalonError
from avalon.games import game_put
from avalon.mp3 import get_mp3_roles_path
from avalon.rules import get_rules

from api_utils import HTTPError


AVALON_BLUEPRINT = Blueprint('avalon', __name__)
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

    if len(request.json) != 1:
        return make_response("Only 1 vote required ('assassin') !", 400)

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        return make_response("Game's id {} does not exist !".format(game_id), 400)

    if game["nb_quest_unsend"] == 5:
        return make_response("Game is over because 5 consecutive laps have been passed : Red team won !", 400)

    assassin_id = list(request.json)[0]
    vote_assassin = request.json[assassin_id]

    if assassin_id not in game["players"]:
        return make_response("Player {} is not in this game !".format(assassin_id), 400)

    if "assassin" not in r.RethinkDB().table("players").get(assassin_id).run():
        return make_response("Player {} is not 'assassin' !".format(assassin_id), 400)

    if vote_assassin not in game["players"]:
        return make_response("Player {} is not in this game !".format(vote_assassin), 400)

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        return make_response("Game's id {} does not exist !".format(game_id), 400)

    result = game.get("result")
    if not result:
        return make_response("Game's status is not established !", 400)

    if not result["status"]:
        return make_response("Games's status should be 'true' (ie blue team won) !", 400)

    if "guess_merlin_id" in result:
        return make_response("Merlin already chosen !", 400)

    result["guess_merlin_id"] = vote_assassin
    if db_get_value("players", vote_assassin, "role") == "merlin":
        result["status"] = False

    updated_game = r.RethinkDB().table("games").get(game_id).update(
        {"result": result},
        return_changes=True
    )["changes"][0]["new_val"].run()

    updated_game.update(
        {
            "players": resolve_key_id(table="players", list_id=updated_game["players"]),
            "quests": resolve_key_id(table="quests", list_id=updated_game["quests"])
        }
    )

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
    """list player_id."""

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
