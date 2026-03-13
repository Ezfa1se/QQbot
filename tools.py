import re

from user import Servant, Character
import json


def read_servant_from_txt(file_path='servants.txt'):
    servants = []

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        for s in data:
            servant = Servant(
                rank=s["排名"],
                jp_name=s["日文名"],
                en_name=s["英文名"],
                anime=s["作品"]
            )

            servants.append(servant)

    return servants


def read_characters_from_txt(file_path='anime_characters.txt'):
    characters = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if line:
                data = json.loads(line)

                character = Character(
                    rank=data["rank"],
                    name=data["name"],
                    en_name=data["en_name"],
                    description=data["description"],
                    enneagram=data["enneagram"],
                    mbti=data["mbti"],
                    disc=data["disc"]
                )

                characters.append(character)

    return characters


def find_character(cid):
    with open("character.jsonlines", "r", encoding="utf8") as f:

        for line in f:
            data = json.loads(line)
            if data["id"] == cid:
                return data

    return None


def find_subject_ids(cid):
    subject_ids = []
    with open("subject-characters.jsonlines", "r", encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            if data["character_id"] == cid:
                subject_ids.append(data["subject_id"])
    return subject_ids


def find_subject(sid):
    with open("subject.jsonlines", "r", encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            if data["id"] == sid:
                name = data.get("name_cn") or data.get("name")
                tags = [t["name"] for t in data.get("tags", [])]
                meta_tags = data.get("meta_tags", [])
                return {
                    "name": name,
                    "tags": tags,
                    "meta_tags": meta_tags
                }
    return None


def build_keywords(character):
    keywords = set()
    # 名字
    keywords.add(character.name)
    keywords.update(character.tags)
    keywords.update(character.subjects)
    return keywords


def load_tags():
    with open("id_tags.json", "r", encoding="utf-8") as f:
        return json.load(f)


def parse_infobox(infobox_str):
    result = {}
    if not infobox_str:
        return result
    lines = infobox_str.splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        line = line[1:]  # 去掉 |
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            continue
        result[key] = value

    return result