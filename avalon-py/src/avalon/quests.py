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
        raise AvalonError("Game is over because 5 consecutive laps have been passed: Red team won !")

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
