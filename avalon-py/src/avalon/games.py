from random import shuffle, choice

import rethinkdb as r

from avalon.db_utils import resolve_key_id
from avalon.exception import AvalonError
from avalon.rules import get_rules


def game_put(payload):
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
    if set(payload) != {"names", "roles"}:
        raise AvalonError("Only 'names' and 'roles' are required!")

    if not isinstance(payload["names"], list) or not isinstance(payload["roles"], list):
        raise AvalonError("Both 'names' and 'roles' must be a list!")

    rules = get_rules()
    min_nb_player = int(min(rules, key=int))
    max_nb_player = int(max(rules, key=int))

    if not min_nb_player <= len(payload["names"]) <= max_nb_player:
        raise AvalonError("Player number should be between {} and {}!".format(min_nb_player, max_nb_player))

    if len(payload["names"]) != len(set(payload["names"])):
        raise AvalonError("Players name should be unique!")

    if [player for player in payload["names"] if (player.isspace() or player == "")]:
        raise AvalonError("Players' name cannot be empty!")

    if len(payload["roles"]) != len(set(payload["roles"])):
        raise AvalonError("Players role should be unique!")

    available_roles = ("oberon", "morgan", "mordred", "perceval")  #TODO: ne devrait pas etre en dur
    for role in payload["roles"]:
        if role not in available_roles:
            raise AvalonError("Players role should be {}, {}, {} or {}!".format(*available_roles))

    if "morgan" in payload["roles"] and "perceval" not in payload["roles"]:
        raise AvalonError("'morgan' is selected but 'perceval' is not!")

    if "perceval" in payload["roles"] and "morgan" not in payload["roles"]:
        raise AvalonError("'perceval' is selected but 'morgan' is not!")

    # find rules
    game_rules = rules[str(len(payload["names"]))]

    if len([role for role in payload["roles"] if role != "perceval"]) > game_rules["red"]:
        raise AvalonError("Too many red roles chosen!")

    # add roles to players
    players = roles_and_players(payload, game_rules["red"], game_rules["blue"])

    # find players
    list_id_players = r.RethinkDB().table("players").insert(players).run()["generated_keys"]

    # find quests
    list_id_quests = r.RethinkDB().table("quests").insert(game_rules["quests"]).run()["generated_keys"]

    inserted_game = r.RethinkDB().table("games").insert(
        {
            "players": list_id_players,
            "quests": list_id_quests,
            "current_id_player": list_id_players[choice(range(len(payload["names"])))],
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

    return inserted_game


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
