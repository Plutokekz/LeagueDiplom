import os
from typing import Tuple, Any

import pytz
import cassiopeia
import cassiopeia as cass
import datapipelines
from cassiopeia import GameMode
from cassiopeia.core.match import Participant
from merakicommons.container import SearchError

path = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-1])
cass.apply_settings(os.path.join(path, "cassiopeia.json"))


class SummonerNotFoundException(Exception):

    def __init__(self, summoner, message):
        self.summoner = summoner
        self.message = message
        super.__init__(message)


def get_summoner(name: str, region: str = "EUW") -> cassiopeia.Summoner:
    try:
        return cass.get_summoner(name=name, region=region)
    except datapipelines.common.NotFoundError:
        raise SummonerNotFoundException(name, "Summoner with the given name not found in the region")


def save_profile_image(summoner: cassiopeia.Summoner) -> Tuple[Any, str]:
    _path = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    _path = os.path.join(_path, "diploma", "images", "tmp.png")
    with open(_path, "wb") as fp:
        summoner.profile_icon.image.save(fp)
    return summoner.profile_icon.name if summoner.profile_icon.name else "", _path


def get_summoner_division(summoner: cassiopeia.Summoner) -> (str, str):
    rank = summoner.league_entries.fives
    return rank.division, rank.tier


def find_summoner_in_match(match: cassiopeia.Match, summoner: cassiopeia.Summoner) -> (
        Participant, bool):
    participant = None
    try:
        participant = match.red_team.participants.search(summoner).pop(0)
    except SearchError:
        pass
    if participant:
        return participant, match.red_team.win
    return match.blue_team.participants.search(summoner).pop(0), match.blue_team.win


def get_stats(participant: Participant) -> dict:
    return {'vs': participant.stats.vision_score,
            'minions': participant.stats.total_minions_killed,
            'dmg': participant.stats.total_damage_dealt,
            'kda': f"{participant.stats.kills}/{participant.stats.deaths}/{participant.stats.assists}",
            'gold': participant.stats.gold_earned}


def get_last_match(summoner: cassiopeia.Summoner):
    match = summoner.match_history.filter(lambda x: x.mode == GameMode.aram or x.mode == GameMode.classic).pop(0)
    participant, win = find_summoner_in_match(match, summoner)
    date = match.creation.astimezone(pytz.timezone('Europe/Berlin')).strftime('%d.%m.%Y %H:%M:%S')
    data = {'date': date,
            'duration': match.duration,
            'champion': participant.champion.name,
            'win': win}
    data.update(get_stats(participant))
    return data


def get_summoner_profile_dict(name: str) -> dict:
    summoner = get_summoner(name)
    image_name, _path = save_profile_image(summoner)
    rank = get_summoner_division(summoner)
    data = {'level': summoner.level,
            'name': summoner.name,
            'image': _path.replace("\\", "/"),
            'image_name': image_name,
            'division': rank[0],
            'tier': rank[1]}
    data.update(get_last_match(summoner))
    return data


if __name__ == "__main__":
    s = get_summoner_profile_dict("SaItysurprise")
    print(s)
