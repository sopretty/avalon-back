from flask import Blueprint, jsonify, make_response, request
from flask_cors import CORS
import rethinkdb as r

from avalon.db_utils import db_connect, db_get_value, db_update_value

from games import game_get


QUESTS_BLUEPRINT = Blueprint("quests", __name__)
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

    if r.RethinkDB().table("games").get(game_id).run()["nb_quest_unsend"] < 4:
        update_current_id_player(game_id)
        db_update_value("games", game_id, "nb_quest_unsend", db_get_value("games", game_id, "nb_quest_unsend") + 1)

        return game_get(game_id)

    if r.RethinkDB().table("games").get(game_id).run()["nb_quest_unsend"] == 4:
        db_update_value("games", game_id, "nb_quest_unsend", db_get_value("games", game_id, "nb_quest_unsend") + 1)
        r.RethinkDB().table("games").get(game_id).update(
            {"result": {"status": False}},
            return_changes=True)["changes"][0]["new_val"].run()

        return game_get(game_id)

    if r.RethinkDB().table("games").get(game_id).run()["nb_quest_unsend"] == 5:
        return make_response("Game is over because 5 consecutive laps have been passed : Red team won !", 400)


@QUESTS_BLUEPRINT.route("/games/<string:game_id>/quests/<int:quest_number>", methods=["DELETE", "GET", "POST", "PUT"])
def quests_(game_id, quest_number):
    """list player_id."""

    if request.method == "DELETE":
        return quest_delete(game_id, quest_number)

    if request.method == "GET":
        return quest_get(game_id, quest_number)

    if request.method == "POST":
        return quest_post(game_id, quest_number)

    if request.method == "PUT":
        return quest_put(game_id, quest_number)


def quest_delete(game_id, quest_number):

    id_quest_number = db_get_value("games", game_id, "quests")[quest_number]

    return r.RethinkDB().table("quests").get(id_quest_number).replace(
        r.RethinkDB().row.without("votes", "status"), return_changes=True)["changes"][0]["new_val"].run()


def quest_get(game_id, quest_number):

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        return make_response("Game's id {} does not exist !".format(game_id), 400)

    quest = r.RethinkDB().table("quests").get(game["quests"][quest_number]).run()

    if quest["status"] is None:
        return make_response("The vote number {} is not finished !".format(quest_number), 400)

    return jsonify(quest)


def quest_post(game_id, quest_number):

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        return make_response("Game's id {} does not exist !".format(game_id), 400)

    quest = r.RethinkDB().table("quests").get(game["quests"][quest_number]).run()

    if game["nb_quest_unsend"] == 5:
        return make_response("Game is over because 5 consecutive laps have been passed : Red team won !", 400)

    if "result" in game:
        return make_response("Game is over !", 400)

    if game["current_quest"] != quest_number:
        return make_response("Only vote number {} is allowed !".format(game["current_quest"]), 400)

    if "status" not in quest:
        return make_response("Vote number {} is not established !".format(quest_number), 400)

    if quest["status"] is not None:
        return make_response("Vote number {} is finished !".format(quest_number), 400)

    if len(request.json) != 1:
        return make_response("Only one vote allowed !", 400)

    if list(request.json)[0] not in list(quest["votes"]):
        return make_response(
            "Player {} is not allowed to vote !".format(list(request.json)[0]),
            400
        )

    if quest["votes"][list(request.json)[0]] is not None:
        return make_response("Player {} has already voted !".format(list(request.json)[0]), 400)

    if not isinstance(list(request.json.values())[0], bool):
        return make_response("Vote should be a boolean !", 400)

    quest["votes"].update(request.json)

    list_vote = list(quest["votes"].values())
    if not list_vote.count(None):
        quest["status"] = not list_vote.count(False) >= quest["nb_votes_to_fail"]
        game["current_id_player"] = game["players"][
            (game["players"].index(game["current_id_player"]) + 1) % len(game["players"])
        ]
        game["nb_quest_unsend"] = 0
        game["current_quest"] = game["current_quest"] + 1

    if len(quest["votes"]) != quest["nb_players_to_send"]:
        r.RethinkDB().table("quests").get(game["quests"][quest_number]).update({"votes": None}).run()

    quest_replace = r.RethinkDB().table("quests").get(game["quests"][quest_number]).replace(
        quest,
        return_changes=True
    )["changes"][0]["new_val"].run()

    list_status = [
        quest.get("status") for quest in r.RethinkDB().table("quests").get_all(r.RethinkDB().args(game["quests"])).run()
    ]

    if list_status.count(False) >= 3:
        game["result"] = {"status": False}

    if list_status.count(True) >= 3:
        game["result"] = {"status": True}

    if not list_vote.count(None):
        r.RethinkDB().table("games").get(game_id).replace(game).run()

    return jsonify(quest_replace)


def quest_put(game_id, quest_number):

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        return make_response("Game's id {} does not exist !".format(game_id), 400)

    quest = r.RethinkDB().table("quests").get(game["quests"][quest_number]).run()

    if game["nb_quest_unsend"] == 5:
        return make_response("Game is over because 5 consecutive laps have been passed : Red team won !", 400)

    if "result" in game:
        return make_response("Game is over !", 400)

    if game["current_quest"] != quest_number:
        return make_response("Vote number {} is already established !".format(quest_number), 400)

    if ("status" in quest or "votes" in quest) and quest["status"] is not None:
        return make_response("Only vote number {} is allowed !".format(game["current_quest"]), 400)

    if game["nb_quest_unsend"] == 5:
        return make_response("Game is over because 5 consecutive laps have been passed : Red team won !", 400)

    for player_id in request.json:
        if player_id not in game["players"]:
            return make_response("Player {} is not in this game !".format(player_id), 400)

    id_quest_number = game["quests"][quest_number]
    nb_players_to_send = db_get_value("quests", id_quest_number, "nb_players_to_send")
    if len(request.json) != nb_players_to_send:
        return make_response(
            "Quest number {} needs {} votes !".format(quest_number, nb_players_to_send),
            400
        )

    if "status" in quest:
        r.RethinkDB().table("quests").get(id_quest_number).update({"votes": None}).run()

    return jsonify(
        r.RethinkDB().table("quests").get(id_quest_number).update(
            {
                "votes": {player_id: None for player_id in request.json},
                "status": None
            },
            return_changes=True
        )["changes"][0]["new_val"].run()
    )
