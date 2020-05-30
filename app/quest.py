from random import shuffle

from flask import Blueprint, jsonify, make_response, request, send_file, current_app
from flask_cors import CORS
import rethinkdb as r

from bdd_utils import bdd_connect, bdd_get_value, bdd_update_value
from pylib import board

QUEST_BLUEPRINT = Blueprint('quest', __name__)
CORS(QUEST_BLUEPRINT)

QUEST_BLUEPRINT.before_request(bdd_connect)


def update_turn(game_id):
    """This function update turn of the game game_id."""

    list_id_players = bdd_get_value("games", game_id, "players")

    # update current_ind_player
    current_ind_player = bdd_get_value("games", game_id, "current_ind_player")
    next_ind_player = (current_ind_player + 1) % len(list_id_players)
    bdd_update_value("games", game_id, "current_ind_player", next_ind_player)

    # update current_id_player
    bdd_update_value("games", game_id, "current_id_player", list_id_players[next_ind_player])

    # update current_name_player
    current_name_player = bdd_get_value("players", list_id_players[next_ind_player], "name")
    bdd_update_value("games", game_id, "current_name_player", current_name_player)


@QUEST_BLUEPRINT.route("/<string:game_id>/quest_unsend", methods=["POST"])
def quest_unsend(game_id):
    """This function sends new quest of the game <game_id>.
        - method: POST
        - route: /<game_id>/quest_unsend
        - payload example: None
        - response example: board
    """

    # update turn
    update_turn(game_id)

    # update nb_quest_unsend
    bdd_update_value("games", game_id, "nb_quest_unsend", bdd_get_value("games", game_id, "nb_quest_unsend") + 1)

    return board(game_id)


@QUEST_BLUEPRINT.route("/<string:game_id>/quest/<int:quest_id>", methods=["DELETE", "GET", "POST", "PUT"])
def quest(game_id, quest_id):
    """list player_id."""

    if request.method == "DELETE":
        return quest_delete(game_id, quest_id)

    if request.method == "GET":
        return quest_get(game_id, quest_id)

    if request.method == "POST":
        return quest_post(game_id, quest_id)

    if request.method == "PUT":
        return quest_put(game_id, quest_id)


def quest_delete(game_id, quest_id):

    quests = bdd_get_value("games", game_id, "quests")
    del quests[quest_id]["votes"]
    bdd_update_value("games", game_id, "quests", quests)

    response = make_response("", 204)
    response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
    return response


def quest_get(game_id, quest_id):

    quests = bdd_get_value("games", game_id, "quests")

    if quests[quest_id]["status"] is None:
        response = make_response("The vote number {} is not finished !".format(quest_id), 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    votes = list(quests[quest_id]["votes"].values())
    shuffle(votes)

    status = quests[quest_id]["status"]
    return jsonify({
        "votes": votes,
        "status": status
    })


def quest_post(game_id, quest_id):

    quests = bdd_get_value("games", game_id, "quests")

    if "status" not in quests[quest_id]:
        response = make_response("The vote number {} is not established !".format(quest_id), 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if quests[quest_id]["status"] is not None:
        response = make_response("The vote number {} is finished !".format(quest_id), 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if len(request.json) != 1:
        response = make_response("Only one vote allowed !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if list(request.json.keys())[0] not in bdd_get_value("games", game_id, "players"):
        response = make_response(
            "This player {} is not allowed to vote !".format(list(request.json.keys())[0]),
            400
        )
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if not isinstance(list(request.json.values())[0], bool):
        response = make_response("Vote should be a boolean !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response


    quests[quest_id]["votes"].update(request.json)

    list_vote = list(quests[quest_id]["votes"].values())

    if not list_vote.count(None):
        quests[quest_id]["status"] = not list_vote.count(False) >= quests[quest_id]["fail"]

        # update turn
        update_turn(game_id)

        # update nb_quest_unsend
        bdd_update_value("games", game_id, "nb_quest_unsend", 0)

        # update current_quest
        bdd_update_value("games", game_id, "current_quest", bdd_get_value("games", game_id, "current_quest") + 1)

    bdd_update_value("games", game_id, "quests", quests)

    response = make_response("", 204)
    response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
    return response


def quest_put(game_id, quest_id):

    for player_id in request.json:
        if player_id not in bdd_get_value("games", game_id, "players"):
            response = make_response("The player {} is not in this game !".format(player_id), 400)
            response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
            return response

    quests = bdd_get_value("games", game_id, "quests")
    if len(request.json) != quests[quest_id]["quest"]:
        response = make_response(
            "The quest number {} needs {} votes !".format(quest_id, quests[quest_id]["quest"]),
            400
        )
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    quests[quest_id]["votes"] = {player_id: None for player_id in request.json}
    quests[quest_id]["status"] = None
    bdd_update_value("games", game_id, "quests", quests)

    response = make_response("", 204)
    response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
    return response
