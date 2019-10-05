import rethinkdb as r

# host = "127.0.0.1"
# port = 8080
# with r.RethinkDB().connect(host='localhost', port=28015) as conn:
#     r.RethinkDB().table_create("rules").run(conn)
#     r.RethinkDB().table("rules").insert([
#         {"nb_player": 5, "BLUE": 3, "RED": 2, "q1": 2, "q2": 3, "q3": 2, "q4": 3, "q5": 3},
#         {"nb_player": 6, "BLUE": 4, "RED": 2, "q1": 2, "q2": 3, "q3": 4, "q4": 3, "q5": 4},
#         {"nb_player": 7, "BLUE": 4, "RED": 3, "q1": 2, "q2": 3, "q3": 3, "q4": 4, "q5": 4},
#         {"nb_player": 8, "BLUE": 5, "RED": 3, "q1": 3, "q2": 4, "q3": 4, "q4": 5, "q5": 5},
#         {"nb_player": 9, "BLUE": 6, "RED": 3, "q1": 3, "q2": 4, "q3": 4, "q4": 5, "q5": 5},
#         {"nb_player": 10, "BLUE": 6, "RED": 4, "q1": 3, "q2": 4, "q3": 4, "q4": 5, "q5": 5}]).run(conn)


r.RethinkDB().connect('localhost', 28015).repl()
r.RethinkDB().db('test').table_create('tv_shows').run()
r.RethinkDB().table('tv_shows').insert({ 'name': 'Star Trek TNG' }).run()
