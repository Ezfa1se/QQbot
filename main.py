from flask import Flask, request
import requests
from command import *
from tools import read_characters_from_txt, read_servant_from_txt
import re
import time
import random
from ids import character_ids

INIT_HIT_NUM = 10
tags_map = load_tags()
vip_qq_num = []
war_states = {}
# 初始配置
existing_users = {}
# 读取所有老婆
all_characters = read_characters_from_txt()
existing_characters = set()  # 用set更快
# 读取所有从者
all_servants = read_servant_from_txt()
existing_servants = set()

app = Flask(__name__)
NAPCAT_API = "http://127.0.0.1:3000/send_group_msg"
guessing_character = False
character_map = {}
hit_num = INIT_HIT_NUM
Known_hit = []


@app.route("/", methods=["POST"])
def receive():
    global guessing_character
    global character_map
    global hit_num
    global Known_hit
    data = request.json
    print("收到消息:", data)

    if data.get("message_type") == "group":

        group_id = data["group_id"]
        message = data["raw_message"]
        user_id = data["user_id"]
        user_name = data["sender"]["nickname"]

        # 不存在用户就创建
        if user_id not in existing_users:
            existing_users[user_id] = User(userid=user_id, username=user_name)

        user = existing_users[user_id]

        # 打招呼
        if "hello" in message:

            reply = "你好，我是Don，试试召唤老婆吧~"

        # 抽老婆
        elif "抽老婆" in message or "召唤老婆" in message:

            if user.waifu_avi <= 0:
                reply = "对不起，您今天已经没有抽老婆次数了"

            else:
                user.waifu_avi -= 1

                character = add_waifu(user, all_characters, existing_characters)

                if character is None:
                    reply = "所有老婆已经被抽完了"

                else:
                    reply = f"叮~  抽取成功!\n{user.username} 抽到了老婆：{character.name}"

        elif "查看老婆" in message:
            if not user.characters:
                reply = "你还没有老婆呢，快去抽一个吧！"
            else:
                names = [c.name for c in user.characters]
                reply = f"你的老婆有：\n" + "\n".join(names)

        elif "介绍" in message:
            target = message.replace("介绍", "").strip()
            if not target:
                reply = "请在“介绍”后输入角色名字，例如：介绍雷姆"
            else:
                found = None
                for c in existing_characters:
                    if target in c.name:
                        found = c
                        break
                if found:
                    reply = f"{found.name}\nAKA: {found.en_name}\n{found.description}"
                else:
                    reply = "这个角色希腊奶哦"
        elif "查看从者" in message or "介绍从者" in message:
            if not user.have_servant or user.servant is None:
                reply = f"{user.username}, 你还没有召唤从者呢，"
            else:
                s = user.servant
                reply = (
                    f"{user.username}的从者：\n"
                    f"Rank：{s.rank}\n"
                    f"{s.jp_name} ({s.en_name})\n"
                    f"作品：{s.anime}"
                )
        elif "抽从者" in message or "召唤从者" in message:
            if user.have_servant:
                reply = f"你已经有从者：{user.servant.jp_name}，不要再抽啦"
            else:
                result = add_servant(user, all_servants, existing_servants)
                reply = result

        elif "牛老婆" in message or "ntr" in message or "NTR" in message:
            match = re.search(r'qq=(\d+)', message)
            if not match:
                reply = "请@要宣战的对象"
            else:
                target_id = int(match.group(1))
                if target_id not in existing_users:
                    reply = "未找到该用户"
                elif target_id == user_id:
                    reply = "不要牛自己啦！"
                elif target_id in war_states:
                    reply = "该用户正在被牛呢，不要再牛了"
                else:
                    target = existing_users[target_id]
                    if not user.have_servant:
                        reply = "你没有从者，无法牛别人"
                    elif not target.characters:
                        reply = f"{target.username} 对方没有老婆可以牛"
                    elif user.waifu_convert <= 0:
                        reply = "你的牛老婆次数不足"
                    else:

                        user.waifu_convert -= 1
                        war_states[target_id] = {
                            "attacker": user_id,
                            "time": time.time()
                        }
                        reply = f"你正在攻略{target.username}的老婆！\n正在等待{target.username}的回击\n若一分钟内未回击，可以进行夺取"
        elif "回击" in message:
            if user_id not in war_states:
                reply = "没有人在NTR你"
            else:
                state = war_states[user_id]
                attacker = existing_users[state["attacker"]]
                if not user.have_servant:
                    reply = "你没有从者，无法回击"
                else:
                    atk_rank = attacker.servant.rank - attacker.ability
                    def_rank = user.servant.rank - user.ability

                    if atk_rank < def_rank - 10:  # 攻击方更强
                        if random.random() < 0.5:
                            reply = f"经历一番艰难的战斗后,{user.servant.en_name}成功战胜了对方从者，守住了你的老婆"
                        else:
                            waifu = rob_waifu(attacker, user)
                            reply = f"{attacker.servant.en_name}过于强大，{user.servant.en_name}拼尽全力无法战胜，你的老婆{waifu}被{attacker.username}夺取"
                    elif atk_rank < def_rank:
                        reply = f"{attacker.servant.en_name}与{user.servant.en_name}展开一番激烈的战斗，成功守护了你的的老婆"
                    elif atk_rank > def_rank + 10:  # 防守方更强
                        if attacker.characters:
                            waifu = rob_waifu(user, attacker)
                            reply = f"你的从者{user.servant.en_name}轻松击退了对方，获得了{attacker.username}的老婆 {waifu}"
                        else:
                            reply = f"你的从者{user.servant.en_name}轻松击退了对方"
                    else:
                        if random.random() < 0.5:
                            reply = f"你的从者{user.servant.en_name}表现英勇，守住了{user.username}的老婆"
                        else:
                            if attacker.characters:
                                waifu = rob_waifu(user, attacker)
                                reply = f"你的从者{user.servant.en_name}受到了幸运女神的庇护，阻止了{attacker.username}的攻击，并且获得了他的老婆{waifu}"
                            else:
                                reply = f"{user.servant.en_name}轻松阻止了{attacker.username}的攻击"
                    del war_states[user_id]

        elif "夺取" in message:
            found = None
            for defender_id, state in war_states.items():
                if state["attacker"] == user_id:
                    found = (defender_id, state)
                    break
            if not found:
                reply = "你没有在牛别人"
            else:
                defender_id, state = found
                defender = existing_users[defender_id]
                if time.time() - state["time"] < 60:
                    reply = "攻略中，请稍后"
                else:
                    atk_rank = user.servant.rank
                    if defender.servant is None:
                        waifu = rob_waifu(user, defender)
                        reply = f"夺取成功！你获得了{defender.username}的老婆{waifu}"
                    else:
                        def_rank = defender.servant.rank
                        if atk_rank < def_rank:
                            waifu = rob_waifu(user, defender)
                            reply = f"夺取成功！你获得了{defender.username}的老婆{waifu}"
                        else:
                            if random.random() < 0.5:
                                reply = f"对方的从者{defender.servant.en_name}敏锐地发现了你的行动，阻止了Master的老婆被牛"
                            else:
                                waifu = rob_waifu(user, defender)
                                reply = f"夺取成功！你获得了{defender.username}的老婆{waifu}"
                    del war_states[defender_id]
        elif user.have_servant and "杀死从者" in message:
            damage = round(random.random() * 10)
            killed_name = user.servant.en_name
            user.have_servant = False
            user.servant = None
            user.ability -= damage
            reply = f"如同言峰绮礼背刺Lancer一样，你把武器对准了你的从者{killed_name}\n你失去了从者{killed_name}，并受到了{damage}点伤害"
        elif "禁忌之力" in message:
            if user.userid in vip_qq_num:
                user.ability += 99
                user.waifu_avi += 99
                user.waifu_convert += 99
                saber = Character(0, "阿尔托莉雅·潘德拉贡（传说级）", "Altria Pendragon", "Rem", "无法显示", "无法显示",
                                  "无法显示")
                reply = "你召唤了禁忌之力！\n\nuser.ability += 99\nuser.waifu_avi += 99\nuser.waifu_convert += 99\n\n"
                if saber not in existing_characters:
                    existing_characters.add(saber)
                    user.characters.append(saber)
                    reply += "传说级saber已加入你的宝库"
            else:
                user.ability -= 10
                reply = "凡人之躯无法承受禁忌之力。攻击力-10"
        elif "查询攻击力" in message:
            reply=f"你的攻击力加成为{user.ability}"
        elif "2229563129" in message and "投降" in message and guessing_character == True:
            guessing_character = False
            reply = f"答案是：{character_map['name']}\n{character_map['summary']}"

        elif "2229563129" in message and "提示" in message and guessing_character == True:
            if hit_num <= 0:
                reply = "没有提示机会"
            else:
                hit_num -= 1
                reply, Known_hit = hint(character_map, Known_hit)

        elif "2229563129" in message and guessing_character == True:
            reply, guessing_character, Known_hit, hit_num = guess(user, message, character_map, guessing_character,
                                                                  Known_hit, hit_num)
        elif "2229563129" in message and "猜角色规则" in message:
            reply = "说猜角色可以开始游戏\n可以猜测角色、角色属性、角色作品、作品属性\n√为符合，×为不符合或未找到\n提示共10次，每猜中一次提示数+1\n使用提示越少，猜出奖励越多"
        elif "2229563129" in message and "猜角色" in message:
            character_map = generate_character(character_ids, tags_map)
            print(character_map)
            guessing_character = True
            hit_num = INIT_HIT_NUM
            reply = "准备好了，快来猜吧"

        elif "2229563129" in message:
            reply = "对不起，Don希腊奶哦~\n试试下面这些指令\n抽老婆\n介绍xx\n抽从者\n查看从者\n@我猜角色"
        else:
            return {"status": "ok"}

        # 发送消息
        requests.get(
            NAPCAT_API,
            params={
                "group_id": group_id,
                "message": reply
            }
        )
    return {"status": "ok"}


app.run(host="0.0.0.0", port=5000)
