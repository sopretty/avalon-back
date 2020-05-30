from pydub import AudioSegment


def create_mp3():
    """Create mp3 all files depending on roles in the game."""

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
            mp3_combined += AudioSegment.from_mp3("resources/{}".format(mp3))

        mp3_combined.export("resources/{}.mp3".format('-'.join(sorted(list_roles))), format="mp3")
