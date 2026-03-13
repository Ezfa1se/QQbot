from typing import List, Optional


class Character:
    def __init__(self, rank: int, name: str, en_name: str, description: str,
                 enneagram: str, mbti: str, disc: str):
        self.rank = rank
        self.name = name
        self.en_name = en_name
        self.description = description
        self.enneagram = enneagram
        self.mbti = mbti
        self.disc = disc

    def __eq__(self, other):
        if not isinstance(other, Character):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Servant:
    def __init__(self, rank: int, jp_name: str, en_name: str, anime: str,
                 ):
        self.rank = rank
        self.jp_name = jp_name
        self.en_name = en_name
        self.anime = anime


class User:
    def __init__(self, userid: int, username: str, characters: list[Character] = None, attacking: bool = False,
                 waifu_avi: int = 5, waifu_convert: int = 5, have_servant: bool = False, servant: Servant = None,
                 ability: int = 0):
        self.userid = userid
        self.username = username
        self.characters = characters if characters is not None else []
        self.attacking = attacking
        self.waifu_avi = waifu_avi
        self.waifu_convert = waifu_convert
        self.have_servant = have_servant
        self.servant = servant
        self.ability = ability

    def __str__(self):
        return f"User(userid={self.userid}, username='{self.username}', characters={self.characters})"


class Infobox:
    def __init__(self,
                 cn_name: str = "",
                 aliases: Optional[List[str]] = None,
                 gender: str = "",
                 birthday: str = "",
                 blood_type: str = "",
                 height: str = "",
                 weight: str = "",
                 bwh: str = "",
                 source: str = ""):
        self.cn_name = cn_name
        self.aliases = aliases or []
        self.gender = gender
        self.birthday = birthday
        self.blood_type = blood_type
        self.height = height
        self.weight = weight
        self.bwh = bwh
        self.source = source


class guess_character:
    def __init__(self, id, role, name, infobox, summary, comments, collects, tags=None):
        self.id = id
        self.role = role
        self.name = name
        self.infobox = infobox
        self.summary = summary
        self.comments = comments
        self.collects = collects
        self.tags = tags if tags else []



