from flask import Blueprint, jsonify, request
from flask_cors import CORS

from avalon.db_utils import db_connect
from avalon.exception import AvalonError
from avalon.quests import quest_send, quest_unsend

from api_utils import HTTPError


QUESTS_BLUEPRINT = Blueprint("quests", __name__)
CORS(QUESTS_BLUEPRINT)

QUESTS_BLUEPRINT.before_request(db_connect)


@QUESTS_BLUEPRINT.route("/games/<string:game_id>/quest_unsend", methods=["POST"])
def quest_unsend_(game_id):
    """This function sends new quest of the game <game_id>.
        - method: POST
        - route: /<game_id>/quest_unsend
        - payload example: None
        - response example: board
    """
    try:
        game_updated = quest_unsend(game_id=game_id)
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return jsonify(game_updated)


@QUESTS_BLUEPRINT.route("/games/<string:game_id>/quests/<int:quest_number>", methods=["DELETE", "GET", "POST", "PUT"])
def quest_send_(game_id, quest_number):

    try:
        game_updated = quest_send(
            method=request.method,
            payload=request.json,
            game_id=game_id,
            quest_number=quest_number
        )
    except AvalonError as error:
        raise HTTPError(str(error), status_code=400) from error

    return jsonify(game_updated)
