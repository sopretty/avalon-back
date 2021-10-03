import rethinkdb as r

from avalon.exception import AvalonError


def db_connect():
    """This function opens the connection to the database."""

    r.RethinkDB().connect("rethinkdb", 28015).repl()
    # r.RethinkDB().connect("0.0.0.0", 28015).repl()


def resolve_key_id(table, list_id):

    list_players = list(r.RethinkDB().table(table).get_all(*list_id).run())
    dict_players = {dict_player["id"]: dict_player for dict_player in list_players}

    return [dict_players[ident] for ident in list_id]


def db_get_game(game_id):
    """This function visualize the game of the <game_id>"""

    if not game_id:
        return db_get_table(table_name="games")

    game = r.RethinkDB().table("games").get(game_id).run()
    if not game:
        raise AvalonError("Game's id {} does not exist !".format(game_id))

    game.update(
        {
            "players": resolve_key_id(table="players", list_id=game["players"]),
            "quests": resolve_key_id(table="quests", list_id=game["quests"])
        }
    )

    return game


def db_get_table(table_name):
    """This function return the table associated to the current game."""

    return list(r.RethinkDB().table(table_name).run())


def db_get_value(table, ident, key):
    """This function finds the key value in the table."""

    return r.RethinkDB().table(table).get(ident)[key].run()


def db_update_value(table, ident, key, value):
    """This function updates the key value in the table."""

    return r.RethinkDB().table(table).get(ident).update({key: value}).run()


def restart_db(payload_tables):

    if not isinstance(payload_tables, list):
        raise AvalonError("Payload should be a list!")

    list_tables = ("games", "players", "quests", "users")
    for table in payload_tables:
        if table not in list_tables:
            raise AvalonError("Table {} should be in {}!".format(table, list_tables))

        if table in r.RethinkDB().db("test").table_list().run():
            r.RethinkDB().table_drop(table).run()

        # initialize table
        r.RethinkDB().table_create(table).run()

    return ""
