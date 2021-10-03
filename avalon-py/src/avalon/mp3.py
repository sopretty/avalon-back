import importlib.resources as pkg_resources
from pathlib import Path

from pydub import AudioSegment

from avalon.db_utils import db_get_value
from avalon.exception import AvalonError
from .resources import audio


def create_mp3(output_mp3_path="resources"):
    """Create mp3 all files depending on roles in the game"""

    Path(output_mp3_path).mkdir(parents=True, exist_ok=True)

    #TODO: les roles ne devraient pas etre en dur
    list_all_roles = [
        [],
        ["morgan"],
        ["oberon"],
        ["mordred"],
        ["morgan", "oberon"],
        ["morgan", "mordred"],
        ["oberon", "mordred"],
        ["morgan", "oberon", "mordred"]
    ]

    for list_roles in list_all_roles:

        list_mp3 = ["init.mp3", "serv_mord.mp3"]
        if "oberon" in list_roles:
            list_mp3.append("oberon.mp3")
        list_mp3.append("red_identi.mp3")

        if "morgan" in list_roles:
            list_mp3.append("add_per_mor.mp3")

        list_mp3.append("serv_mord.mp3")
        if "mordred" in list_roles:
            list_mp3.append("mordred.mp3")
        list_mp3.extend(["merlin_identi.mp3", "end.mp3"])

        mp3_combined = AudioSegment.empty()
        for mp3 in list_mp3:
            with pkg_resources.path(audio, mp3) as mp3_path:
                mp3_combined += AudioSegment.from_mp3(mp3_path)

        mp3_path_file = Path(output_mp3_path, "_{}.mp3".format('-'.join(sorted(list_roles)))).as_posix()
        mp3_combined.export(mp3_path_file, format="mp3")


def get_mp3_roles_path(game_id, output_mp3_path="resources"):

    # find role of each player
    list_roles = [
        db_get_value("players", player_id, "role") for player_id in db_get_value("games", game_id, "players") \
        if db_get_value("players", player_id, "role") not in ("blue", "merlin", "perceval", "red")
    ]

    name_roles = "-".join(sorted(list_roles))
    mp3_roles_path = Path(output_mp3_path, "_{}.mp3".format(name_roles))

    if not mp3_roles_path.exists():
        raise AvalonError("Mp3 file doesn't exist for this game!")

    return mp3_roles_path.as_posix()
