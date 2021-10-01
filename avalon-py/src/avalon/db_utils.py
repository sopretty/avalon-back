import rethinkdb as r


def db_connect():
    """This function opens the connection to the database."""

    r.RethinkDB().connect("rethinkdb", 28015).repl()
    # r.RethinkDB().connect("0.0.0.0", 28015).repl()


def resolve_key_id(table, list_id):

    list_players = list(r.RethinkDB().table(table).get_all(*list_id).run())
    dict_players = {dict_player["id"]: dict_player for dict_player in list_players}

    return [dict_players[ident] for ident in list_id]


def db_get_value(table, ident, key):
    """This function finds the key value in the table."""

    return r.RethinkDB().table(table).get(ident)[key].run()


def db_update_value(table, ident, key, value):
    """This function updates the key value in the table."""

    return r.RethinkDB().table(table).get(ident).update({key: value}).run()
