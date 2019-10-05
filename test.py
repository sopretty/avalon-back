import rethinkdb as r

host = "rethinkdb"
port = 28015

player_id = "7538ec10-aced-43d5-98c0-5ec6b398692e"


r.RethinkDB().connect('localhost', 28015).repl()



r.RethinkDB().table("games").get()[key].run(conn)

#with r.RethinkDB().connect(host=host, port=port) as conn:
print(list(r.RethinkDB().table("players").filter({"id": player_id}).run())[0]["role"])

