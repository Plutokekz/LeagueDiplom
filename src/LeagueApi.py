import os
import datetime
import pytz
import cassiopeia
import cassiopeia as cass
import datapipelines
from cassiopeia import GameMode
from cassiopeia.core.match import Participant
from merakicommons.container import SearchError


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


def save_profile_image(summoner: cassiopeia.Summoner) -> str:
    path = "\\".join(os.path.abspath(__file__).split("\\")[:-2])
    with open(os.path.join(path, "diploma", "images", "tmp.png"), "wb") as fp:
        summoner.profile_icon.image.save(fp)
    return summoner.profile_icon.name


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
    image_name = save_profile_image(summoner)
    rank = get_summoner_division(summoner)
    data = {'level': summoner.level,
            'name': summoner.name,
            'image': "images/tmp.png",
            'image_name': image_name,
            'division': rank[0],
            'tier': rank[1]}
    data.update(get_last_match(summoner))
    return data


if __name__ == "__main__":
    s = get_summoner_profile_dict("SaItysurprise")
    print(s)