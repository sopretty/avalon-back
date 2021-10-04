import rethinkdb as r

from avalon.db_utils import db_get_value, db_update_value, db_get_game
from avalon.exception import AvalonError


def update_current_id_player(game_id):
    """This function update 'current_id_player' of the game game_id."""

    list_id_players = db_get_value(
        table="games",
        ident=game_id,
        key="players"
    )

    list_current_id_player = db_get_value(
        table="games",
        ident=game_id,
        key="current_id_player"
    )

    current_ind_player = list_id_players.index(list_current_id_player)
    next_ind_player = (current_ind_player + 1) % len(list_id_players)
    db_update_value(
        table="games",
        ident=game_id,
        key="current_id_player",
        value=list_id_players[next_ind_player]
    )


def quest_unsend(game_id):
    """This function sends new quest of the game <game_id>"""

    nb_quest_unsend = db_get_value(
        table="games",
        ident=game_id,
        key="nb_quest_unsend"
    )

    if nb_quest_unsend == 5:
        raise AvalonError("Game is over because 5 consecutive laps have been passed: Red team won!")

    if nb_quest_unsend < 4:
        update_current_id_player(game_id=game_id)
        value = 1 + db_get_value(
            table="games",
            ident=game_id,
            key="nb_quest_unsend"
        )
        db_update_value(
            table="games",
            ident=game_id,
            key="nb_quest_unsend",
            value=value
        )

    if nb_quest_unsend == 4:
        value = 1 + db_get_value(
            table="games",
            ident=game_id,
            key="nb_quest_unsend"
        )
        db_update_value(
            table="games",
            ident=game_id,
            key="nb_quest_unsend",
            value=value
        )
        r.RethinkDB().table("games").get(game_id).update(
            {
                "result": {
                    "status": False
                }
            },
            return_changes=True
        )["changes"][0]["new_val"].run()

    game_updated = db_get_game(game_id=game_id)

    return game_updated


def quest_send(method, payload, game_id, quest_number):

    list_methods = [
        "DELETE",
        "GET",
        "POST",
        "PUT"
    ]

    if method not in list_methods:
        raise AvalonError("Method should be in '{}'!".format(list_methods))

    if method == "DELETE":
        game_updated = quest_delete(
            game_id=game_id,
            quest_number=quest_number
        )

    elif method == "GET":
        game_updated = quest_get(
            game_id=game_id,
            quest_number=quest_number
        )

    elif method == "POST":
        game_updated = quest_post(
            payload=payload,
            game_id=game_id,
            quest_number=quest_number
        )

    elif method == "PUT":
        game_updated = quest_put(
            payload=payload,
            game_id=game_id,
            quest_number=quest_number
        )

    return game_updated


def quest_delete(game_id, quest_number):

    id_quest_number = db_get_value(
        table="games",
        ident=game_id,
        key="quests"
    )[quest_number]

    game_updated = r.RethinkDB().table("quests").get(id_quest_number).replace(
        r.RethinkDB().row.without("votes", "status"),
        return_changes=True
    )["changes"][0]["new_val"].run()

    return game_updated


def quest_get(game_id, quest_number):

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        raise AvalonError("Game's id '{}' does not exist!".format(game_id))

    game_updated = r.RethinkDB().table("quests").get(game["quests"][quest_number]).run()

    if game_updated["status"] is None:
        raise AvalonError("The vote number '{}' is not finished!".format(quest_number))

    return game_updated


def quest_post(payload, game_id, quest_number):

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        raise AvalonError("Game's id '{}' does not exist!".format(game_id))

    if game["nb_quest_unsend"] == 5:
        raise AvalonError("Game is over because 5 consecutive laps have been passed : Red team won!")

    if "result" in game:
        raise AvalonError("Game is over!")

    if game["current_quest"] != quest_number:
        raise AvalonError("Only vote number {} is allowed!".format(game["current_quest"]))

    quest = r.RethinkDB().table("quests").get(game["quests"][quest_number]).run()

    if "status" not in quest:
        raise AvalonError("Vote number '{}' is not established!".format(quest_number))

    if quest["status"] is not None:
        raise AvalonError("Vote number '{}' is finished!".format(quest_number))

    if len(payload) != 1:
        raise AvalonError("Only one vote allowed!")

    if list(payload)[0] not in list(quest["votes"]):
        raise AvalonError("Player '{}' is not allowed to vote!".format(list(payload)[0]))

    if quest["votes"][list(payload)[0]] is not None:
        raise AvalonError("Player '{}' has already voted!".format(list(payload)[0]))

    if not isinstance(list(payload.values())[0], bool):
        raise AvalonError("Vote should be a boolean!")

    quest["votes"].update(payload)

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

    game_updated = r.RethinkDB().table("quests").get(game["quests"][quest_number]).replace(
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

    return game_updated


def quest_put(payload, game_id, quest_number):

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        raise AvalonError("Game's id '{}'' does not exist!".format(game_id))

    if game["nb_quest_unsend"] == 5:
        raise AvalonError("Game is over because 5 consecutive laps have been passed : Red team won!")

    if "result" in game:
        raise AvalonError("Game is over!")

    if game["current_quest"] != quest_number:
        raise AvalonError("Vote number {} is already established!".format(quest_number))

    quest = r.RethinkDB().table("quests").get(game["quests"][quest_number]).run()

    if ("status" in quest or "votes" in quest) and quest["status"] is not None:
        raise AvalonError("Only vote number '{}'' is allowed!".format(game["current_quest"]))

    for player_id in payload:
        if player_id not in game["players"]:
            raise AvalonError("Player '{}' is not in this game!".format(player_id))

    id_quest_number = game["quests"][quest_number]
    nb_players_to_send = db_get_value(
        table="quests",
        ident=id_quest_number,
        key="nb_players_to_send"
    )

    if len(payload) != nb_players_to_send:
        raise AvalonError("Quest number '{}' needs '{}' votes!".format(quest_number, nb_players_to_send))

    if "status" in quest:
        r.RethinkDB().table("quests").get(id_quest_number).update({"votes": None}).run()

    game_updated = (
        r.RethinkDB().table("quests").get(id_quest_number).update(
            {
                "votes": {player_id: None for player_id in payload},
                "status": None
            },
            return_changes=True
        )["changes"][0]["new_val"].run()
    )

    return game_updated
