import random
from tools import *
from user import *


def add_waifu(user, all_characters, existing_characters):
    remaining = [
        c for c in all_characters
        if c not in existing_characters
    ]
    if not remaining:
        return None
    chosen = random.choice(remaining)
    existing_characters.add(chosen)
    user.characters.append(chosen)
    return chosen


def add_servant(user, all_servants, existing_servants):
    if user.have_servant:
        return f"{user.username} 已经拥有从者 {user.servant.jp_name}"
    remaining = [
        s for s in all_servants
        if s.jp_name not in existing_servants
    ]
    if not remaining:
        return "所有从者已经被召唤完了"
    chosen = random.choice(remaining)

    user.servant = chosen
    user.have_servant = True

    existing_servants.add(chosen.jp_name)

    return f"登登噔！\n{user.username} 召唤了从者：{chosen.jp_name}\n又名{chosen.en_name},  来自{chosen.anime}的世界"


def rob_waifu(attacker: User, defender: User):
    if not defender.characters:
        return f"{defender.username} 没有老婆可以被抢"
    # 随机选择一个角色
    waifu = random.choice(defender.characters)
    # 从 defender 移除
    defender.characters.remove(waifu)
    # 添加到 attacker
    attacker.characters.append(waifu)
    return waifu.name


def generate_character(character_ids, tags_map):
    cid = random.choice(character_ids)
    char = find_character(cid)
    if not char:
        return None
    tags = tags_map.get(str(cid), [])
    subject_ids = find_subject_ids(cid)
    subjects = []
    subject_tags = []
    for sid in subject_ids[:3]:
        subject = find_subject(sid)
        if subject:
            subjects.append(subject["name"])
            subject_tags.extend(subject["tags"])
            subject_tags.extend(subject["meta_tags"])
    infobox_dict = parse_infobox(char["infobox"])
    name = infobox_dict.get("简体中文名", char["name"])
    return {
        "id": cid,
        "name": name,
        "infobox": infobox_dict,
        "summary": char["summary"],
        "tags": tags,
        "subjects": subjects,
        "subject_tags": list(set(subject_tags))  # 去重
    }


def hint(character, Known_hit):
    hints = []
    # 角色属性
    if character["tags"]:
        hints.append(random.choice(character["tags"]))
    # 作品标签 / meta_tags
    if character.get("subject_tags"):
        hints.append("作品提示：" + random.choice(character["subject_tags"]))
    # infobox 信息
    ignore = {"简体中文名", "引用来源", "别名"}
    for key, value in character["infobox"].items():
        if key in ignore:
            continue
        if not value:
            continue
        hints.append(f"{key}：{value}")

    available_hints = [h for h in hints if h not in Known_hit]
    if not available_hints:
        return "没有更多提示了", Known_hit
    random_hint = random.choice(available_hints)
    Known_hit.append(random_hint)
    return random_hint, Known_hit


def guess(user, message, character, guessing_character, Known_hit, hit_num):
    text = message.split(']', 1)[1].strip()
    if len(character["name"]) >= 5 and len(text) >= 2:
        if text in character["name"]:
            user.ability += 10
            guessing_character = False
            return f"恭喜你猜对了！战斗力+10\n{character['summary']}", guessing_character, Known_hit, hit_num
    else:
        if text == character["name"]:
            user.ability += hit_num
            guessing_character = False
            return f"恭喜你猜对了！剩余了{hit_num}次提示机会，已转化为你的战斗力\n{character['summary']}", guessing_character, Known_hit, hit_num
    if text in character["tags"]:
        if ("作品提示：" + text not in Known_hit) and text not in Known_hit:
            hit_num += 1
            Known_hit.append(text)
        return "√", guessing_character, Known_hit, hit_num
    if text in character.get("subject_tags", []):
        if ("作品提示：" + text not in Known_hit) and text not in Known_hit:
            hit_num += 1
            Known_hit.append(text)
        return "√", guessing_character, Known_hit, hit_num
    for value in character["infobox"].values():
        if text in value:
            if ("作品提示：" + text not in Known_hit) and text not in Known_hit:
                hit_num += 1
                Known_hit.append(text)
            return "√", guessing_character, Known_hit, hit_num
    for subject in character["subjects"]:
        if text in subject:
            return f"猜中了作品！", guessing_character, Known_hit, hit_num
    return "×", guessing_character, Known_hit, hit_num
