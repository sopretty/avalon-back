from random import shuffle

from flask import Blueprint, jsonify, make_response, request, current_app
from flask_cors import CORS

from db_utils import db_connect, db_get_value, db_update_value
from games import game_get

QUESTS_BLUEPRINT = Blueprint('quests', __name__)
CORS(QUESTS_BLUEPRINT)

QUESTS_BLUEPRINT.before_request(db_connect)


def update_current_id_player(game_id):
    """This function update 'current_id_player' of the game game_id."""

    list_id_players = db_get_value("games", game_id, "players")
    current_ind_player = list_id_players.index(db_get_value("games", game_id, "current_id_player"))
    next_ind_player = (current_ind_player + 1) % len(list_id_players)
    db_update_value("games", game_id, "current_id_player", list_id_players[next_ind_player])


@QUESTS_BLUEPRINT.route("/games/<string:game_id>/quest_unsend", methods=["POST"])
def quest_unsend(game_id):
    """This function sends new quest of the game <game_id>.
        - method: POST
        - route: /<game_id>/quest_unsend
        - payload example: None
        - response example: board
    """

    update_current_id_player(game_id)

    # update nb_quest_unsend
    db_update_value("games", game_id, "nb_quest_unsend", db_get_value("games", game_id, "nb_quest_unsend") + 1)

    return game_get(game_id)


@QUESTS_BLUEPRINT.route("/games/<string:game_id>/quests/<int:quest_id>", methods=["DELETE", "GET", "POST", "PUT"])
def quests_(game_id, quest_id):
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

    quests = db_get_value("games", game_id, "quests")
    del quests[quest_id]["votes"]
    db_update_value("games", game_id, "quests", quests)

    response = make_response("", 204)
    response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
    return response


def quest_get(game_id, quest_id):

    quests = db_get_value("games", game_id, "quests")

    if quests[quest_id]["status"] is None:
        response = make_response("The vote number {} is not finished !".format(quest_id), 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    # votes = list(quests[quest_id]["votes"].values())
    # shuffle(votes)

    # status = quests[quest_id]["status"]
    # return jsonify({
    #     "votes": votes,
    #     "status": status
    # })

    return jsonify(quests[quest_id])


def quest_post(game_id, quest_id):

    quests = db_get_value("games", game_id, "quests")

    if "status" not in quests[quest_id]:
        response = make_response("Vote number {} is not established !".format(quest_id), 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if quests[quest_id]["status"] is not None:
        response = make_response("Vote number {} is finished !".format(quest_id), 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if len(request.json) != 1:
        response = make_response("Only one vote allowed !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if list(request.json.keys())[0] not in db_get_value("games", game_id, "players"):
        response = make_response(
            "Player {} is not allowed to vote !".format(list(request.json.keys())[0]),
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
        quests[quest_id]["status"] = not list_vote.count(False) >= quests[quest_id]["nb_votes_to_fail"]

        update_current_id_player(game_id)

        # update nb_quest_unsend
        db_update_value("games", game_id, "nb_quest_unsend", 0)

        # update current_quest
        db_update_value("games", game_id, "current_quest", db_get_value("games", game_id, "current_quest") + 1)

    list_status = [quest.get("status") for quest in quests]

    if list_status.count(False) >= 3:
        db_update_value("games", game_id, "result", {"status": False})

    if list_status.count(True) >= 3:
        db_update_value("games", game_id, "result", {"status": True})

    db_update_value("games", game_id, "quests", quests)

    return jsonify(quests[quest_id])


def quest_put(game_id, quest_id):

    for player_id in request.json:
        if player_id not in db_get_value("games", game_id, "players"):
            response = make_response("Player {} is not in this game !".format(player_id), 400)
            response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
            return response

    quests = db_get_value("games", game_id, "quests")
    if len(request.json) != quests[quest_id]["nb_players_to_send"]:
        response = make_response(
            "Quest number {} needs {} votes !".format(quest_id, quests[quest_id]["nb_players_to_send"]),
            400
        )
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    quests[quest_id]["votes"] = {player_id: None for player_id in request.json}
    quests[quest_id]["status"] = None
    db_update_value("games", game_id, "quests", quests)

    return jsonify(quests[quest_id])
