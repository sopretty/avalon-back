from random import choice, sample

import requests as req


def new_vote(game_id, url, result=None):

    game = req.get("{}games/{}".format(url, game_id)).json()
    list_players_quest = sample(game["players"], game["quests"][game["current_quest"]]["nb_players_to_send"])

    req.put(
        "{}games/{}/quests/{}".format(url, game_id, game["current_quest"]),
        json=[dictio["id"] for dictio in list_players_quest]
    )

    print("\n\n")

    nb_votes = 0
    if result is not None:
        nb_votes = game["quests"][game["current_quest"]]["nb_votes_to_fail"]
        if result:
            nb_votes = len(list_players_quest) - (game["quests"][game["current_quest"]]["nb_votes_to_fail"] - 1)

    for ind, player in enumerate(list_players_quest):
        print("\n", req.get("{}games/{}".format(url, game_id)).json()["quests"][game["current_quest"]])
        if ind < nb_votes:
            req.post(
                "{}games/{}/quests/{}".format(url, game_id, game["current_quest"]),
                json={player["id"]: result}
            )
        else:
            req.post(
                "{}games/{}/quests/{}".format(url, game_id, game["current_quest"]),
                json={player["id"]: choice([True, True, False])}
            )
    print("\n", req.get("{}games/{}".format(url, game_id)).json()["quests"][game["current_quest"]])

    req.get("{}games/{}".format(url, game_id))


def quests(game_id, url, result=None):

    while "result" not in req.get("{}games/{}".format(url, game_id)).json():
        new_vote(game_id, url, result)
        req.get("{}games/{}".format(url, game_id))


def complete_game(roles, nb_players=choice(range(5, 11)), vote_assassin=None, result=None, url="http://localhost:5000/"):

    put_games = {"names": ["player{}".format(nb+1) for nb in range(nb_players)], "roles": roles}
    req_put_game = req.put("{}games".format(url), json=put_games)

    game_id = req_put_game.json()["id"]

    # req.get("{}games/{}/mp3".format(url, game_id))

    quests(game_id=game_id, url=url, result=result)

    req.get("{}games/{}".format(url, game_id))

    if vote_assassin is False:
        assassin_id = [dico for dico in req_put_game.json()["players"] if "assassin" in dico][0]["id"]
        merlin = [dico for dico in req_put_game.json()["players"] if dico["role"] == "merlin"][0]["id"]
        req.post("{}games/{}/guess_merlin".format(url, game_id), json={assassin_id: merlin})

    req.get("{}games/{}".format(url, game_id))


def main():

    # put_restart_db = ["games", "players", "quests", "users"]
    # req.put("{}restart_db".format(url), json=put_restart_db)

    complete_game(roles=[])


if __name__ == '__main__':

    main()
