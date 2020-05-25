"""This functions are used is the RESTful web service of Avalon"""

import os
from random import shuffle, choice

import rethinkdb as r
from flask import Blueprint, Flask, jsonify, make_response, request, abort, send_file, Response, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS


AVALON_BLUEPRINT = Blueprint('avalon', __name__)
CORS(AVALON_BLUEPRINT)

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


@AVALON_BLUEPRINT.before_request
def before_first_request_func():
    """This function opens the connection to the database."""

    r.RethinkDB().connect("rethinkdb", 28015).repl()


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

    return jsonify({"request": "succeeded"})


@AVALON_BLUEPRINT.route('/view/<table_name>', methods=['GET'])
def view(table_name):
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

    response = {table_name: []}
    cursor = r.RethinkDB().table(table_name).run()
    for document in cursor:
        response[table_name].append(document)

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

    # create new game in table games
    insert = r.RethinkDB().table("games").insert([{"players": [], "rules": {}}]).run()
    game_id = insert["generated_keys"][0]

    # find rules
    rules = list(r.RethinkDB().table("rules").filter({"nb_player": len(request.json["names"])}).run())[0]
    del rules["id"]
    del rules["nb_player"]

    # update rules
    bdd_update_value("games", game_id, "rules", rules)

    # add roles to players
    players = roles_and_players(request.json, rules["red"], rules["blue"])

    # find players
    list_id_players = []
    for player in players:
        list_id_players.append(r.RethinkDB().table("players").insert(player).run()["generated_keys"][0])

    # update players
    bdd_update_value("games", game_id, "players", list_id_players)

    # update nb_player_to_send
    bdd_update_value("games", game_id, "nb_player_to_send", {key: val for key, val in rules.items()\
                                                             if key[:5] == "quest"})

    # update nb_echec_to_fail
    bdd_update_value("games", game_id, "nb_echec_to_fail", {key: val for key, val in rules.items()\
                                                            if key[:5] == "echec"})

    # update quest_result
    bdd_update_value("games", game_id, "quest_result", ["", "", "", "", ""])

    # update nb_mission_unsend
    bdd_update_value("games", game_id, "nb_mission_unsend", 0)

    # update current_ind_player
    ind = choice(range(len(request.json["names"])))
    bdd_update_value("games", game_id, "current_ind_player", ind)

    # update current_id_player
    current_id_player = list(r.RethinkDB().table("players").filter({"ind_player": ind}).run())[0]["id"]
    bdd_update_value("games", game_id, "current_id_player", current_id_player)

    # update current_name_player
    current_name_player = list(r.RethinkDB().table("players").filter({"ind_player": ind}).run())[0]["name"]
    bdd_update_value("games", game_id, "current_name_player", current_name_player)

    # update current_quest
    bdd_update_value("games", game_id, "current_quest", 1)

    # update nb_mission_unsend
    bdd_update_value("games", game_id, "nb_mission_unsend", 0)

    # find players to return
    list_players = []
    for player_id in list_id_players:
        list_players.append(list(r.RethinkDB().table("players").get_all(player_id).run())[0])

    return jsonify({"players": list_players, "id": game_id})


@AVALON_BLUEPRINT.route('/<game_id>/mp3', methods=['GET'])
def post_mp3(game_id):
    """This function creates the mp3file depending on roles of players.
        - method: GET
        - route: /<game_id>/mp3
        - payload example:
        - response example: response.mpga
    """

    # # find role of each player
    # list_roles = []
    # for player_id in bdd_get_value("games", game_id, "players"):
    #     list_roles.append(list(r.RethinkDB().table("players").filter({"id": player_id}).run())[0]["role"])

    # # create mp3file
    # create_mp3(list_roles)

    # return send_file("resources/roles.mp3", attachment_filename='roles.mp3', mimetype='audio/mpeg')
    return send_file("resources/test_song.mp3", attachment_filename='roles.mp3', mimetype='audio/mpeg')


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
                                "nb_mission_unsend": 0,
                                "nb_player_to_send": {
                                    "quest1": 2,
                                    "quest2": 3,
                                    "quest3": 2,
                                    "quest4": 3,
                                    "quest5": 3
                                }
                            }
    """

    # find board of the <game_id>
    return jsonify({
        "nb_mission_unsend": bdd_get_value("games", game_id, "nb_mission_unsend"),
        "current_id_player": bdd_get_value("games", game_id, "current_id_player"),
        "current_ind_player": bdd_get_value("games", game_id, "current_ind_player"),
        "current_name_player": bdd_get_value("games", game_id, "current_name_player"),
        "current_quest": bdd_get_value("games", game_id, "current_quest"),
        "nb_player_to_send": bdd_get_value("games", game_id, "nb_player_to_send"),
        "nb_echec_to_fail": bdd_get_value("games", game_id, "nb_echec_to_fail")
    })


@AVALON_BLUEPRINT.route('/<game_id>/mission', methods=['POST'])
def mission(game_id):
    """This function sends new mission of the game <game_id>.
        - method: POST
        - route: /<game_id>/mission
        - payload example1: {
                                "status": "unsend"
                            }
        - response example1: {
                                "request": "succeeded"
                             }
        - payload example2: {
                                "status": "send"
                            }
        - response example2: {
                                 "players": [
                                     {
                                         "id": "147ff90f-9988-45f3-bf39-c98d9fc48e3a",
                                         "ind_player": 0,
                                         "name": "name1"
                                     },
                                     {
                                         ...
                                     },
                                     {
                                         "id": "d8cc0522-5389-4d15-9f2c-9c377b6260df",
                                         "ind_player": 4,
                                         "name": "name5"
                                     }
                                 ]
                             }
    """

    try:
        if request.json["status"] not in ["unsend", "send"]:
            return jsonify({"request": "unsucceeded",
                            "message": "'status' is not 'send' or 'unsend'"})
    except KeyError:
        return jsonify({"request": "unsucceeded",
                        "message": "'status' is missing"})

    # ----> check current_quest
    # ----> check nb_mission_unsend
    # ----> check nb_player in payload == quest_i


    # update current_ind_player
    nb_player = len(bdd_get_value("games", game_id, "players"))
    current_ind_player = bdd_get_value("games", game_id, "current_ind_player")
    next_ind_player = (current_ind_player + 1) % nb_player
    bdd_update_value("games", game_id, "current_ind_player", next_ind_player)

    # update current_id_player
    current_id_player = list(r.RethinkDB().table("players").filter({"ind_player": next_ind_player}).run())[0]["id"]
    bdd_update_value("games", game_id, "current_id_player", current_id_player)

    # update current_name_player
    current_name_player = list(r.RethinkDB().table("players").filter({"ind_player": next_ind_player}).run())[0]["name"]
    bdd_update_value("games", game_id, "current_name_player", current_name_player)

    if request.json["status"] == "send":

        # update nb_mission_unsend
        nb_mission_unsend = 0
        bdd_update_value("games", game_id, "nb_mission_unsend", nb_mission_unsend)

        # update current_quest
        current_quest = bdd_get_value("games", game_id, "current_ind_player")
        bdd_update_value("games", game_id, "current_quest", current_quest + 1)

        # find players
        list_players = []
        for id_player in bdd_get_value("games", game_id, "players"):
            list_players.append({"id": bdd_get_value("players", id_player, "id"),
                                 "ind_player": bdd_get_value("players", id_player, "ind_player"),
                                 "name": bdd_get_value("players", id_player, "name")})

        return jsonify({"players": list_players})

    # update nb_mission_unsend
    nb_mission_unsend = bdd_get_value("games", game_id, "nb_mission_unsend") + 1
    bdd_update_value("games", game_id, "nb_mission_unsend", nb_mission_unsend)

    return jsonify({"request": "succeeded"})


@AVALON_BLUEPRINT.route('/<game_id>/vote', methods=['POST'])
def vote(game_id):
    """This function sends new mission of the game <game_id>.
        - method: POST
        - route: /<game_id>/vote
        - payload example1: {
                                "vote": ["SUCCESS", "FAIL"]
                            }
        - response example1: {
                                 "result": "FAIL",
                                 "vote": [
                                     "FAIL",
                                     "SUCCESS"
                                 ]
                             }
        - payload example2: {
                                "vote": ["SUCCESS", "SUCCESS"]
                            }
        - response example2: {
                                 "result": "SUCCESS",
                                 "vote": [
                                     "SUCCESS",
                                     "SUCCESS"
                                 ]
                             }
    """

    list_vote = request.json["vote"]
    shuffle(list_vote)

    dict_nb_echec_to_fail = bdd_get_value("games", game_id, "nb_echec_to_fail")
    nb_echec_to_fail = dict_nb_echec_to_fail["echec"+str(bdd_get_value("games", game_id, "current_quest"))]

    result = "SUCCESS"
    if list_vote.count("FAIL") >= nb_echec_to_fail:
        result = "FAIL"

    # update quest_result
    quest_result = bdd_get_value("games", game_id, "quest_result")
    quest_result[bdd_get_value("games", game_id, "current_quest") - 1] = result
    bdd_update_value("games", game_id, "quest_result", quest_result)


    return jsonify({"vote": list_vote,
                    "result": result})



########################################################################################################################
########################################################################################################################
########################################################################################################################


def bdd_get_value(table, ident, key):
    """This function finds the key value in the table."""

    return r.RethinkDB().table(table).get(ident)[key].run()


def bdd_update_value(table, ident, key, value):
    """This function updates the key value in the table."""

    return r.RethinkDB().table(table).get(ident).update({key: value}).run()


def roles_and_players(dict_names_roles, max_red, max_blue):
    """Check the validity of proposed roles.
    cases break rules: - 1. morgan in the game but Perceval is not
                       - 2. perceval in the game but Morgan is not
                       - 3. Unvalid role
                       - 4. Too many red in the game (or too many blue in the game, checked but impossible)"""

    if "morgan" in dict_names_roles["roles"] and "perceval" not in dict_names_roles["roles"]:
        print("ERROR !!! morgan is in the game but perceval is not")

    if "perceval" in dict_names_roles["roles"] and "morgan" not in dict_names_roles["roles"]:
        print("ERROR !!! perceval is in the game but morgan is not")

    nb_red, nb_blue = 1, 1
    list_roles = ["merlin", "assassin"]
    for role in dict_names_roles["roles"]:
        if role in ["mordred", "morgan", "oberon"]:
            nb_red += 1
            list_roles.append(role)
        elif role == "perceval":
            nb_blue += 1
            list_roles.append(role)
        else:
            print("ERROR !!! can't add this role: "+str(role))

    if nb_red <= max_red and nb_blue <= max_blue:
        list_roles.extend(["red"]*(max_red-nb_red))
        list_roles.extend(["blue"]*(max_blue-nb_blue))
    else:
        print("ERROR !!! Too many red or blue")

    shuffle(list_roles)

    list_players = []
    for ind, role in enumerate(list_roles):
        if role in ["merlin", "perceval", "blue"]:
            list_players.append({"ind_player": ind, "name": dict_names_roles["names"][ind],
                                 "team": "blue", "role": role})
        else:
            list_players.append({"ind_player": ind, "name": dict_names_roles["names"][ind],
                                 "team": "red", "role": role})

    return list_players


def create_mp3(list_roles):
    """Create mp3 file depending on roles in the game."""

    list_to_merge = ["init.mp3", "serv_mord.mp3"]
    if "oberon" in list_roles:
        list_to_merge.append("oberon.mp3")
    list_to_merge.append("red_identi.mp3")

    if "morgan" in list_roles and "perceval" in list_roles:
        list_to_merge.append("add_per_mor.mp3")

    list_to_merge.append("serv_mord.mp3")
    if "mordred" in list_roles:
        list_to_merge.append("mordred.mp3")
    list_to_merge.extend(["merlin_identi.mp3", "end.mp3"])

    str_command = "cat "
    for mp3 in list_to_merge:
        str_command += "resources/"+mp3+" "
    str_command += " > resources/roles.mp3"

    os.system(str_command)
    mp3_file = open('./resources/roles.mp3', 'rb')
    #os.system("rm -f /resources/roles.mp3")

    return mp3_file



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
