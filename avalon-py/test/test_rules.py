from avalon.rules import get_rules


def test_get_rules():

    rules = get_rules()

    for nb_player, rules_player in rules.items():
        assert 5 <= int(nb_player) <= 10
        assert set(rules_player) == {"blue", "red", "quests"}
