from random import shuffle, choice

from flask import Blueprint, jsonify, make_response, request
from flask_cors import CORS
import rethinkdb as r

from avalon.db_utils import db_connect, db_get_table, resolve_key_id
from avalon.rules import get_rules


GAMES_BLUEPRINT = Blueprint("games", __name__)
CORS(GAMES_BLUEPRINT)

GAMES_BLUEPRINT.before_request(db_connect)


@GAMES_BLUEPRINT.route("/games/<string:game_id>", methods=["GET", "PUT"])
@GAMES_BLUEPRINT.route("/games", methods=["GET", "PUT"])
def games(game_id=None):
    """list player_id."""

    if request.method == "GET":
        return game_get(game_id)

    if request.method == "PUT":
        return game_put()


def game_get(game_id):
    """This function visualize the game of the <game_id>"""

    if not game_id:
        return jsonify(db_get_table(table_name="games"))

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        return make_response("Game's id {} does not exist !".format(game_id), 400)

    game.update(
        {
            "players": resolve_key_id(table="players", list_id=game["players"]),
            "quests": resolve_key_id(table="quests", list_id=game["quests"])
        }
    )

    return jsonify(game)


def game_put():
    """
    This function adds rules and roles to players randomly.
        - method: PUT
        - route: /games
        - payload example: {
                               "names": [
                                   "name1",
                                   "name2",
                                   "name3",
                                   "name4",
                                   "name5"
                               ],
                               "roles": [
                                   "oberon",
                                   "perceval",
                                   "morgan"
                               ]
                           }
        - response example: {
                                "id": "2669a9fe-37c4-4139-ab78-8e3f0d0607d0",
                                "players": [
                                    {
                                        "id": "95763b27-de50-4d39-8ac2-2a7010281788",
                                        "name": "name1",
                                        "role": "assassin",
                                        "team": "red"
                                    },
                                    {
                                        ...
                                    },
                                    {
                                        "id": "83d21d25-f359-4ddc-9048-69ba1e6cf5b5",
                                        "name": "name5",
                                        "role": "morgan",
                                        "team": "red"
                                    }
                                ]
                            }
    """

    if set(request.json) != {"names", "roles"}:
        return make_response("Only 'names' and 'roles' are required !", 400)

    if not isinstance(request.json["names"], list) or not isinstance(request.json["roles"], list):
        return make_response("Both 'names' and 'roles' must be a list !", 400)

    rules = get_rules()
    min_nb_player = int(min(rules, key=int))
    max_nb_player = int(max(rules, key=int))

    if not min_nb_player <= len(request.json["names"]) <= max_nb_player:
        return make_response(
            "Player number should be between {} and {} !".format(min_nb_player, max_nb_player),
            400
        )

    if len(request.json["names"]) != len(set(request.json["names"])):
        return make_response("Players name should be unique !", 400)

    if [player for player in request.json["names"] if (player.isspace() or player == "")]:
        return make_response("Players' name cannot be empty !", 400)

    if len(request.json["roles"]) != len(set(request.json["roles"])):
        return make_response("Players role should be unique !", 400)

    available_roles = ("oberon", "morgan", "mordred", "perceval")  #TODO: ne devrait pas etre en dur
    for role in request.json["roles"]:
        if role not in available_roles:
            return make_response("Players role should be {}, {}, {} or {} !".format(*available_roles), 400)

    if "morgan" in request.json["roles"] and "perceval" not in request.json["roles"]:
        return make_response("'morgan' is selected but 'perceval' is not !", 400)

    if "perceval" in request.json["roles"] and "morgan" not in request.json["roles"]:
        return make_response("'perceval' is selected but 'morgan' is not !", 400)

    # find rules
    game_rules = rules[str(len(request.json["names"]))]

    if len([role for role in request.json["roles"] if role != "perceval"]) > game_rules["red"]:
        return make_response("Too many red roles chosen !", 400)

    # add roles to players
    players = roles_and_players(request.json, game_rules["red"], game_rules["blue"])

    # find players
    list_id_players = r.RethinkDB().table("players").insert(players).run()["generated_keys"]

    # find quests
    list_id_quests = r.RethinkDB().table("quests").insert(game_rules["quests"]).run()["generated_keys"]

    inserted_game = r.RethinkDB().table("games").insert(
        {
            "players": list_id_players,
            "quests": list_id_quests,
            "current_id_player": list_id_players[choice(range(len(request.json["names"])))],
            "current_quest": 0,
            "nb_quest_unsend": 0
        },
        return_changes=True
    )["changes"][0]["new_val"].run()

    inserted_game.update(
        {
            "players": resolve_key_id(table="players", list_id=inserted_game["players"]),
            "quests": resolve_key_id(table="quests", list_id=inserted_game["quests"])
        }
    )

    return jsonify(inserted_game)


def roles_and_players(dict_names_roles, max_red, max_blue):
    """Check the validity of proposed roles.
    cases break rules: - 1. morgan in the game but Perceval is not
                       - 2. perceval in the game but Morgan is not
                       - 3. Unvalid role
                       - 4. Too many red in the game (or too many blue in the game, checked but impossible)"""

    nb_red, nb_blue = 0, 1
    list_roles = ["merlin"]
    for role in dict_names_roles["roles"]:
        if role in ["mordred", "morgan", "oberon"]:
            nb_red += 1
            list_roles.append(role)
        elif role == "perceval":
            nb_blue += 1
            list_roles.append(role)

    list_roles.extend(["red"]*(max_red-nb_red))
    list_roles.extend(["blue"]*(max_blue-nb_blue))

    shuffle(list_roles)

    bool_assassin = True
    list_players = []
    for ind, role in enumerate(list_roles):
        player = {
            "name": dict_names_roles["names"][ind],
            "role": role,
            "team": "blue"
        }

        if role not in ("merlin", "perceval", "blue"):
            player["team"] = "red"
            if bool_assassin:
                bool_assassin = False
                player["assassin"] = True

        list_players.append(player)

    return list_players
