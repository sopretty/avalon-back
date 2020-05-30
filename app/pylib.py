"""This functions are used is the RESTful web service of Avalon"""

from random import shuffle, choice

import rethinkdb as r
from flask import Blueprint, current_app, jsonify, make_response, request, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

from bdd_utils import bdd_connect, bdd_get_value


AVALON_BLUEPRINT = Blueprint('avalon', __name__)
CORS(AVALON_BLUEPRINT)

AVALON_BLUEPRINT.before_request(bdd_connect)

AUTH = HTTPBasicAuth()

USERS = {
    "mathieu": generate_password_hash("lebeaugosse"),
    "romain": generate_password_hash("lala")
}


@AUTH.verify_password
def verify_password(username, password):
    if username in USERS:
        return check_password_hash(USERS.get(username), password)
    return False


@AVALON_BLUEPRINT.route('/')
@AUTH.login_required
def index():
    return "Hello, %s!" % AUTH.username()


@AVALON_BLUEPRINT.route('/restart_bdd', methods=['PUT'])
#@AUTH.login_required
def restart_bdd():
    """
    This function deletes all tables in the post request and initializes them.
        - method: PUT
        - route: /retart_bdd
        - payload example: {
                               "table1": "rules",
                               "table2": "games",
                               "table3": "players"
                           }
        - response example: {
                                "request": "succeeded"
                            }
    """

    for key in request.json.values():
        if key in r.RethinkDB().db('test').table_list().run():
            r.RethinkDB().table_drop(key).run()

        # initialize table
        r.RethinkDB().table_create(key).run()

        # fill rules table
        if key == "rules":
            r.RethinkDB().table("rules").insert([
                {"nb_player": 5, "blue": 3, "red": 2,
                 "quest1": 2, "quest2": 3, "quest3": 2, "quest4": 3, "quest5": 3,
                 "echec1": 1, "echec2": 1, "echec3": 1, "echec4": 1, "echec5": 1},
                {"nb_player": 6, "blue": 4, "red": 2,
                 "quest1": 2, "quest2": 3, "quest3": 4, "quest4": 3, "quest5": 4,
                 "echec1": 1, "echec2": 1, "echec3": 1, "echec4": 1, "echec5": 1},
                {"nb_player": 7, "blue": 4, "red": 3,
                 "quest1": 2, "quest2": 3, "quest3": 3, "quest4": 4, "quest5": 4,
                 "echec1": 1, "echec2": 1, "echec3": 1, "echec4": 2, "echec5": 1},
                {"nb_player": 8, "blue": 5, "red": 3,
                 "quest1": 3, "quest2": 4, "quest3": 4, "quest4": 5, "quest5": 5,
                 "echec1": 1, "echec2": 1, "echec3": 1, "echec4": 2, "echec5": 1},
                {"nb_player": 9, "blue": 6, "red": 3,
                 "quest1": 3, "quest2": 4, "quest3": 4, "quest4": 5, "quest5": 5,
                 "echec1": 1, "echec2": 1, "echec3": 1, "echec4": 2, "echec5": 1},
                {"nb_player": 10, "blue": 6, "red": 4,
                 "quest1": 3, "quest2": 4, "quest3": 4, "quest4": 5, "quest5": 5,
                 "echec1": 1, "echec2": 1, "echec3": 1, "echec4": 2, "echec5": 1}]).run()

    response = make_response("", 204)
    response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
    return response



@AVALON_BLUEPRINT.route('/view/<string:table>', methods=['GET'])
def view(table):
    """
    This function visualizes a table depending on the input <table_name>.
        - method: GET
        - route: /view/<table_name> (table_name is rules, games and players)
        - payload example:
        - response example: {
                                "rules": [
                                    {
                                        "blue": 3,
                                        "echec1": 1,
                                        "echec2": 1,
                                        "echec3": 1,
                                        "echec4": 1,
                                        "echec5": 1,
                                        "id": "5fb71032-7dad-4e48-bb14-7f4fb7c262fa",
                                        "nb_player": 5,
                                        "quest1": 2,
                                        "quest2": 3,
                                        "quest3": 2,
                                        "quest4": 3,
                                        "quest5": 3,
                                        "red": 2
                                    },
                                    {
                                        ...
                                    },
                                    {
                                        "blue": 6,
                                        "echec1": 1,
                                        "echec2": 1,
                                        "echec3": 1,
                                        "echec4": 2,
                                        "echec5": 1,
                                        "id": "f9bffa54-dc75-45f2-b2f8-51ad0c4f397f",
                                        "nb_player": 10,
                                        "quest1": 3,
                                        "quest2": 4,
                                        "quest3": 4,
                                        "quest4": 5,
                                        "quest5": 5,
                                        "red": 4
                                    }
                                ]
                            }
    """
    if table not in ("games", "rules", "players"):
        response = make_response("Table should be 'games', 'players' or 'rules' !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    response = {table: []}
    cursor = r.RethinkDB().table(table).run()
    for document in cursor:
        response[table].append(document)

    return jsonify(response)


@AVALON_BLUEPRINT.route('/games', methods=['PUT'])
def add_roles():
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
                                        "ind_player": 0,
                                        "name": "name1",
                                        "role": "assassin",
                                        "team": "red"
                                    },
                                    {
                                        ...
                                    },
                                    {
                                        "id": "83d21d25-f359-4ddc-9048-69ba1e6cf5b5",
                                        "ind_player": 4,
                                        "name": "name5",
                                        "role": "morgan",
                                        "team": "red"
                                    }
                                ]
                            }
    """

    if set(request.json) != {"names", "roles"}:
        response = make_response("Only 'names' and 'roles' are required !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if not isinstance(request.json["names"], list) or not isinstance(request.json["roles"], list):
        response = make_response("Both 'names' and 'roles' must be a list !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    rules = list(r.RethinkDB().table("rules").run())
    min_nb_player = min(rules, key=lambda x: x["nb_player"])["nb_player"]
    max_nb_player = max(rules, key=lambda x: x["nb_player"])["nb_player"]

    if not min_nb_player <= len(request.json["names"]) <= max_nb_player:
        response = make_response(
            "Player number should be between {} and {} !".format(min_nb_player, max_nb_player),
            400
        )
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if len(request.json["names"]) != len(set(request.json["names"])):
        response = make_response("Players name should be unique !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if len(request.json["roles"]) != len(set(request.json["roles"])):
        response = make_response("Players role should be unique !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    available_roles = ("oberon", "morgan", "mordred", "perceval")  #TODO: ne devrait pas etre en dur
    for role in request.json["roles"]:
        if role not in available_roles:
            response = make_response("Players role should be {}, {}, {} or {} !".format(*available_roles), 400)
            response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
            return response

    if "morgan" in request.json["roles"] and "perceval" not in request.json["roles"]:
        response = make_response("'morgan' is selected but 'perceval' is not !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    if "perceval" in request.json["roles"] and "morgan" not in request.json["roles"]:
        response = make_response("'perceval' is selected but 'morgan' is not !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    # find rules
    game_rules = list(r.RethinkDB().table("rules").filter({"nb_player": len(request.json["names"])}).run())[0]
    del game_rules["id"]
    del game_rules["nb_player"]

    if len([role for role in request.json["roles"] if role != "perceval"]) > game_rules["red"]:
        response = make_response("Too many red roles chosen !", 400)
        response.mimetype = current_app.config["JSONIFY_MIMETYPE"]
        return response

    # add roles to players
    players = roles_and_players(request.json, game_rules["red"], game_rules["blue"])

    # find players
    list_id_players = []
    for player in players:
        list_id_players.append(r.RethinkDB().table("players").insert(player).run()["generated_keys"][0])

    ind = choice(range(len(request.json["names"])))

    # create new game in table games
    insert = r.RethinkDB().table("games").insert([{
        "players": list_id_players,
        "quests": [
            {
                "quest": game_rules["quest{}".format(ind)],
                "fail": game_rules["echec{}".format(ind)],
            } for ind in range(1, 6)
        ],
        "current_ind_player": ind,
        "current_id_player": list(r.RethinkDB().table("players").filter({"ind_player": ind}).run())[0]["id"],
        "current_name_player": list(r.RethinkDB().table("players").filter({"ind_player": ind}).run())[0]["name"],
        "current_quest": 0,
        "nb_quest_unsend": 0
    }]).run()

    # find players to return
    list_players = []
    for player_id in list_id_players:
        list_players.append(list(r.RethinkDB().table("players").get_all(player_id).run())[0])

    return jsonify({"players": list_players, "id": insert["generated_keys"][0]})


@AVALON_BLUEPRINT.route('/<game_id>/mp3', methods=['GET'])
def post_mp3(game_id):
    """This function creates the mp3file depending on roles of players.
        - method: GET
        - route: /<game_id>/mp3
        - payload example:
        - response example: response.mpga
    """

    # find role of each player
    list_roles = []
    for player_id in bdd_get_value("games", game_id, "players"):
        list_roles.append(list(r.RethinkDB().table("players").filter({"id": player_id}).run())[0]["role"])

    name_roles = "-".join(sorted(
        [role for role in list_roles if role not in ("assassin", "blue", "merlin", "perceval", "red")]
    ))

    return send_file("resources/{}.mp3".format(name_roles), attachment_filename="roles.mp3", mimetype="audio/mpeg")


@AVALON_BLUEPRINT.route('/<game_id>/board', methods=['GET'])
def board(game_id):
    """This function visualize the board of the <game_id>.
        - method: GET
        - route: /<game_id>/board
        - payload example:
        - response example: {
                                "current_id_player": "79d33eb2-199c-40a2-8205-27cc3511aede",
                                "current_ind_player": 1,
                                "current_name_player": "name2",
                                "current_quest": 1,
                                "nb_echec_to_fail": {
                                    "echec1": 1,
                                    "echec2": 1,
                                    "echec3": 1,
                                    "echec4": 1,
                                    "echec5": 1
                                },
                                "nb_quest_unsend": 0,
                                "nb_player_to_send": {
                                    "quest1": 2,
                                    "quest2": 3,
                                    "quest3": 2,
                                    "quest4": 3,
                                    "quest5": 3
                                }
                            }
    """

    quests = bdd_get_value("games", game_id, "quests")

    list_status = [quest.get("status") for quest in quests]
    if list_status.count(False) < 3 and list_status.count(True) < 3:
        for quest in quests:
            if "votes" in quest:
                del quest["votes"]

    # find board of the <game_id>
    return jsonify({
        "current_id_player": bdd_get_value("games", game_id, "current_id_player"),
        "nb_quest_unsend": bdd_get_value("games", game_id, "nb_quest_unsend"),
        "current_quest": bdd_get_value("games", game_id, "current_quest"),
        "quests": quests
    })






# @AVALON_BLUEPRINT.route('/<string:game_id>/votes/<string:quest_id>', methods=['GET'])
# @AVALON_BLUEPRINT.route('/<string:game_id>/votes', methods=['GET'])
# def votes(game_id, quest_id=False):
#     """This function sends votes mission of the game <game_id> for the <quest_id>.
#         - method: POST
#         - route: /<game_id>/votes/<quest_id>
#         - payload example1: None
#         - response example1: {
#                                  "result": False,
#                                  "vote": [
#                                      False,
#                                      True
#                                  ]
#                              }
#         - payload example2: None
#         - response example2: {
#                                  "result": True,
#                                  "vote": [
#                                      True,
#                                      True
#                                  ]
#                              }
#     """

#     quest_id_votes = bdd_get_value("games", game_id, "current_quest") - 1
#     if quest_id:
#         quest_id_votes = quest_id

#     votes_id = bdd_get_value("games", game_id, "quests")[quest_id_votes-1]["votes"]

#     list_vote = [vote[1] for vote in votes_id]
#     shuffle(list_vote)

#     return jsonify({"vote": list_vote, "result": bdd_get_value("games", game_id, "quests")[quest_id_votes-1]["result"]})



########################################################################################################################
########################################################################################################################
########################################################################################################################


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

    list_players = []
    for ind, role in enumerate(list_roles):
        if role in ["merlin", "perceval", "blue"]:
            list_players.append(
                {
                    "ind_player": ind,
                    "name": dict_names_roles["names"][ind],
                    "team": "blue",
                    "role": role
                }
            )
        else:
            list_players.append(
                {
                    "ind_player": ind,
                    "name": dict_names_roles["names"][ind],
                    "team": "red",
                    "role": role
                }
            )

    return list_players


########################################################################################################################
########################################################################################################################
########################################################################################################################



# current_app.logger.warning('A warning occurred (%d apples)', 42)
# current_app.logger.error('An error occurred')
# current_app.logger.info('Info')


# def bdd_get_players_value(ident, ind_player, key):
#     """This function finds the key's value in the bdd of players"""
#     with r.RethinkDB().connect(host=host, port=port) as conn:

#         return r.RethinkDB().table("games").get(ident)['players'].filter({"ind_player": ind_player}).run(conn)[0][key]

# @auth_blueprint.login_required
# @avalon_blueprint.route('/<ident>/get/<table>/<key>', methods=['POST'])
# def get(ident, table, key):
#     """This function finds the key's value depending of the table in the bdd"""

#     return r.RethinkDB().table(table).get(ident)[key].run()


#######################################################################################################################
#######################################################################################################################


# @auth_blueprint.verify_password
# def verify_password(username, password):
#     if username in users:
#         return check_password_hash(users.get(username), password)
#     return False

# @avalon_blueprint.route('/<ident>/new_turn', methods=['GET'])
# def new_turn(ident):
#     """This function updates the bdd with a new turn"""

#     with r.RethinkDB().connect(host=host, port=port) as conn:

#         nb_player = len(bdd_get_value(ident, "players"))-1

#         # get current player
#         current_player = bdd_get_value(ident, 'current_player')

#         # get name of current player
#         name_player = bdd_get_players_value(ident, current_player, 'name')

#         # get current turn
#         current_turn = bdd_get_value(ident, "current_turn")

#         # get number of echecs
#         nb_echec_to_fail = 1
#         if current_turn == 4 and nb_player >= 7:
#             nb_echec_to_fail = 2

#         # get number of mission
#         nb_failed_mission = bdd_get_value(ident, "current_echec")

#         # get number of vote
#         nb_in_mission = r.RethinkDB().table("games").get(ident)['rules']['q'+str(current_turn)].run(conn)

#     return jsonify({"name_player": name_player, "turn": current_turn, "nb_echec_to_fail": nb_echec_to_fail,
#                     "nb_failed_mission": nb_failed_mission, "nb_in_mission": nb_in_mission})


# @avalon_blueprint.route('/<ident>/new_mission', methods=['GET'])
# def new_mission(ident):
#     """This function updates the bdd with a new vote"""

#     with r.RethinkDB().connect(host=host, port=port) as conn:

#         nb_player = len(bdd_get_value(ident, "players"))-1

#         # get current player
#         current_player = bdd_get_value(ident, 'current_player')

#         # get name of current player
#         name_player = bdd_get_players_value(ident, current_player, 'name')

#         # get current turn
#         current_turn = bdd_get_value(ident, "current_turn")

#         # get number of echecs
#         nb_echec_to_fail = 1
#         if current_turn == 4 and nb_player >= 7:
#             nb_echec_to_fail = 2

#         # get number of echec
#         nb_failed_mission = bdd_get_value(ident, "current_echec")

#         # get number of vote
#         nb_vote = r.RethinkDB().table("games").get(ident)['rules']['q'+str(current_turn)].run(conn)

#     return jsonify({"name_player": name_player, "turn": current_turn, "nb_echec_to_fail": nb_echec_to_fail,
#                     "nb_failed_mission": nb_failed_mission, "nb_in_mission": nb_in_mission})


# @avalon_blueprint.route('/<ident>/vote', methods=['POST'])
# def vote(ident):
#     """This function gives the answer of a vote"""

#     if request.json["vote"] == "refused":

#         nb_player = len(bdd_get_value(ident, "players"))-1

#         # update current player
#         current_player = bdd_get_value(ident, 'current_player')
#         new_current_player = current_player+1
#         if current_player == nb_player:
#             new_current_player = 0
#         bdd_update_value(ident, "current_player", new_current_player)

#         # update number of echec
#         new_current_echec = bdd_get_value(ident, 'current_echec')+1
#         bdd_update_value(ident, "current_echec", new_current_echec)

#         return jsonify({"request": "succeeded"})

#     return jsonify({"players": bdd_get_value(ident, "players")})


# @avalon_blueprint.route('/<ident>/shuffle_vote', methods=['POST'])
# def shuffle_vote(ident):
#     """This function shuffles vote"""

#     dict_bdd = request.json.copy()
#     nb_player = len(bdd_get_value(ident, "players"))-1

#     # get current turn
#     current_turn = bdd_get_value(ident, "current_turn")

#     # get number of echecs
#     nb_echec_to_fail = 1
#     if current_turn == 4 and nb_player >= 7:
#         nb_echec_to_fail = 2

#     cpt_false = 0
#     for val in dict_bdd.values():
#         if val == "FAIL":
#             cpt_false += 1

#     dict_bdd["result"] = "SUCCESS"
#     if cpt_false >= nb_echec_to_fail:
#         dict_bdd["result"] = "FAIL"

#     bdd_update_value(ident, "mission_"+str(current_turn), dict_bdd)

#     bdd_update_value(ident, "current_turn", current_turn)

#     list_vote = request.json.values()
#     shuffle(list_vote)

#     dict_output = {}
#     for ind, vote in enumerate(list_vote):
#         dict_output["vote"+str(ind+1)] = vote
#     dict_output["result"] = dict_bdd["result"]

#     return jsonify(dict_output)


#######################################################################################################################
#######################################################################################################################


# def create_mp3(list_roles):
#     """Create mp3 file depending on roles in the game"""

#     list_to_merge = ["init.mp3", "serv_mord.mp3"]
#     if "oberon" in list_roles:
#         list_to_merge.append("oberon.mp3")
#     list_to_merge.append("red_identi.mp3")

#     if "morgan" in list_roles and "perceval" in list_roles:
#         list_to_merge.append("add_per_mor.mp3")

#     list_to_merge.append("serv_mord.mp3")
#     if "mordred" in list_roles:
#         list_to_merge.append("mordred.mp3")

#     list_to_merge.extend(["merlin_identi.mp3", "end.mp3"])

#     str_command = "python concat.py "
#     for val in list_to_merge:
#         str_command += "resources/"+val+" "
#     str_command += "> resources/roles.mp3"
#     print(str_command)
#     os.system(str_command)



# @avalon_blueprint.route("/<ident>/mp3_2")
# def streamwav():
#     def generate():
#         with open("data/roles.mp3", "rb") as fwav:
#             data = fwav.read(1024)
#             while data:
#                 yield data
#                 data = fwav.read(1024)
#     return Response(generate(), mimetype="audio/mpeg") # mimetype="audio/x-mp3", mimetype="audio/mp3"

# mp3_file = create_mp3(list_roles)
# print(mp3_file)
# response = make_response(mp3_file)
# response.headers.set('Content-Type', 'audio/mpeg')
# response.headers.set('Content-Disposition', 'attachment', filename='%s.jpg' % pid)
