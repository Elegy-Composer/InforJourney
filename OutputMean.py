from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, RetryAfter, TimedOut, Unauthorized
from time import sleep
from Player import Player
from Data import *

helpString = """join - Join a game
start - Start a game
jizz - Throw a die to move
map - Show the game map
pos - Show Your positon
buy - [no] Buy an item in shop
upgrade - [weapon/armor] Upgrade weapon or armor in blacksmith shop
change - Change weapon or armor
end - Leave shop or blacksmith shop
drink - [no] Drink a potion
mystat - Show your status
showpotion - Show all your potions
showstat - Show status of chosen entity
retire - retire from game
exp - Show your exp
coin - Show your coins
help - Show game help"""

def sending(func):
    def sending_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RetryAfter as e:
            print(f"retry after {e.retry_after} seconds")
            sleep(5)
            return sending_wrapper(*args, **kwargs)
        except TimedOut:
            sleep(5)
            print("time out, sleep 5 seconds")
            # print("try do nothing at time out")
            return sending_wrapper(*args, **kwargs)
        except (Unauthorized):
            #pm failed
            #args[0] is self
            args[0].bot.sendMessage(args[0].id, "Please add me! @inforJourneyBot")
    return sending_wrapper

class Output:
    def __init__(self, bot: Bot, id):
        self.bot = bot
        self.id = id
        self.end_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Leave', callback_data='end')],
        ])
    
    @sending
    def send_help(self):
        self.bot.sendMessage(self.id, helpString)

    @sending
    def send_welcome(self, name):
        self.bot.sendMessage(self.id, f"{name}加入了遊戲", parse_mode="Markdown")

    @sending
    def send_start_game(self):
        self.bot.sendMessage(self.id, "遊戲已開始")

    def tag_user(self, player):
        if player.username:
            return f"@{player.username}"
        else:
            return f"[{player.name}](tg://user?id={player.id})"

    @sending
    def send_player_turn_start(self, player: Player):
        self.bot.sendMessage(self.id, 
            f"換{player.name}了唷 {self.tag_user(player)}\n你目前在第{player.pos}格", 
            parse_mode="Markdown"
        )
    
    @sending
    def send_jizz_result(self, player_name, jizz):
        self.bot.sendMessage(self.id, f"{player_name}骰出了{jizz}.")
    
    @sending
    def send_map(self):
        self.bot.sendPhoto(self.id, open("./Img/raw_map.jpg","rb"))
    
    @sending
    def send_pos(self, name, pos):
        self.bot.sendMessage(self.id, f"{name}目前在第{pos}格")

    @sending
    def send_potion(self, uid, name, potions):
        potions_str = ""
        if not potions:
            potions_str = "無"
        else:
            potions_list = [f"{i}. {str(potion)}" for i, potion in enumerate(potions)]
            potions_str = "\n".join(potions_list)
        self.bot.sendMessage(uid, f"{name}的藥水們:\n{potions_str}")

    @sending
    def send_heal_result(self, player: Player, potion, heal_point):
        self.bot.sendMessage(self.id, f"{player.name}飲用了{potion}\n回復{heal_point}點生命\n{player.name}現在有{player.hp}點生命")

    @sending 
    def send_wrong_argument(self):
        self.bot.sendMessage(self.id, "參數錯誤")

    @sending
    def send_change(self, name, uid, avaliable_items):
        kb_list = []
        for w in avaliable_items:
            kb_list.append([InlineKeyboardButton(text=w.name, callback_data="change "+str(uid)+" "+w.name)])

        if kb_list:
            keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
            self.bot.sendMessage(self.id, f"{name}, 請選擇更換裝備", reply_markup=keyboard)
        else:
            self.bot.sendMessage(self.id, f"{name}沒有可更換的裝備")

    @sending 
    def change_succeed(self, name, item, identifier):
        self.bot.editMessageText(f"{name}已成功裝備{item}", chat_id=identifier[0], message_id=identifier[1])

    @sending
    def send_retire_confirm(self, name):
        self.bot.sendMessage(self.id, f"{name},你確定要退出遊戲嗎?\n確定退出請再次輸入 /retire")

    @sending
    def send_retire(self, name):
        self.bot.sendMessage(self.id, f"{name}離開了遊戲")
    
    @sending
    def send_stat(self, uid):
        kb_list = [
            [InlineKeyboardButton(text="小怪", callback_data="showstat monster"),
            InlineKeyboardButton(text="首領", callback_data="showstat boss")],
            [InlineKeyboardButton(text="玩家", callback_data="showstat player"),
            InlineKeyboardButton(text="武器", callback_data="showstat weapon 0")],
            [InlineKeyboardButton(text="防具", callback_data="showstat armor 0"),
            InlineKeyboardButton(text="道具", callback_data="showstat item")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.sendMessage(uid, "請選擇種類", reply_markup=keyboard)

    @sending
    def stat_category(self, identifier):
        kb_list = [
            [InlineKeyboardButton(text="小怪", callback_data="showstat monster"),
            InlineKeyboardButton(text="首領", callback_data="showstat boss")],
            [InlineKeyboardButton(text="玩家", callback_data="showstat player"),
            InlineKeyboardButton(text="武器", callback_data="showstat weapon 0")],
            [InlineKeyboardButton(text="防具", callback_data="showstat armor 0"),
            InlineKeyboardButton(text="道具", callback_data="showstat item")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇種類", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_monster_stage(self, identifier):
        kb_list = []
        for i in range(4):
            kb_list.append([InlineKeyboardButton(text="階段"+str(i+1), callback_data="showstat monster "+str(i))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_monsters(self, identifier, stage):
        kb_list = []
        for name in Monsters[stage]:
            kb_list.append([InlineKeyboardButton(text=name, callback_data="showstat monster "+stage+" "+name)])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat monster")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_bosses(self, identifier):
        kb_list = []
        for i in range(4):
            kb_list.append([InlineKeyboardButton(text=Bosses[i][0], callback_data="showstat boss "+str(i))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_players(self, players, identifier):
        kb_list = []
        for player in players:
            kb_list.append([InlineKeyboardButton(text=player.name, callback_data="showplayer "+str(player.id))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_items(self, identifier):
        kb_list = []
        for p in Potions:
            kb_list.append([InlineKeyboardButton(text=p, callback_data="showstat item "+p)])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_weapons(self, identifier, page):
        kb_list = []
        weapon_list = list(Weapons.items())
        if page:
            kb_list.append([InlineKeyboardButton(text="<<", callback_data="showstat weapon "+str(page-1))])
        for i in range(page*6, min(page*6+6, len(weapon_list))):
            name, param = weapon_list[i]
            kb_list.append([InlineKeyboardButton(text=name, callback_data="showweapon "+name)])
        if page*6 + 6 < len(weapon_list):
            kb_list.append([InlineKeyboardButton(text=">>", callback_data="showstat weapon "+str(page+1))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_armors(self, identifier, page):
        kb_list = []
        armor_list = list(Armors.items())
        if page:
            kb_list.append([InlineKeyboardButton(text="<<", callback_data="showstat armor "+str(page-1))])
        for i in range(page*6, min(page*6+6, len(armor_list))):
            name, param = armor_list[i]
            kb_list.append([InlineKeyboardButton(text=name, callback_data="showarmor "+name)])
        if page*6 + 6 < len(armor_list):
            kb_list.append([InlineKeyboardButton(text=">>", callback_data="showstat armor "+str(page+1))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText("請選擇", chat_id=identifier[0], message_id=identifier[1], reply_markup=keyboard)

    @sending
    def stat_player(self, uid, player: Player):
        # player_str = "{name}: 等級:{}\n攻:{}, 防:{}, \nHP: {}, 最大HP: {}\n"
        # player_str += "武器:{}\n  攻+{} 防+{}\n防具:{}\n  攻+{} 防+{}\n"
        # player_str += "{name}目前經驗值:{}\n升級所需經驗值:{}\n"
        # player_str += "{name}現在有 {} 金幣"
        print('inside stat_player')
        print('player:')
        print(player)
        player_str = (
            f'{player.name}: 等級:{player.lvl}\n'
            f'攻:{player.atk}, 防:{player.dfd}, \n'
            f'HP: {player.hp}, 最大HP: {player.maxhp}\n'
            f'武器:{player.weapon.name}\n'
            f'  攻+{player.weapon.atk} 防+{player.weapon.dfd}\n'
            f'防具:{player.armor.name}\n'
            f'  攻+{player.armor.atk} 防+{player.armor.dfd}\n'
            f'{player.name}目前經驗值:{player.exp}\n'
            f'升級所需經驗值:{Exps[player.lvl] if player.lvl < len(Exps) else "-"}\n'
            f'{player.name}現在有 {player.coin} 金幣'
        )

        self.bot.sendMessage(uid, player_str)
    
    @sending
    def stat_monster(self, uid, monster_name, monster_data):
        self.bot.sendMessage(uid, (
            f'{monster_name}: 攻:{monster_data[0]}, 防:{monster_data[1]}, HP: {monster_data[2]}\n'
            f'經驗值: {monster_data[3]}, 金幣: {monster_data[4]}\n'
            f'出現等級: {monster_data[5]} ~ {monster_data[6]}'
        ))

    @sending
    def stat_item(self, uid, potion):
        self.bot.sendMessage(uid, f'恢復{"/".join(map(lambda x: str(x), potion))}點生命')

    @sending
    def stat_weapon(self, uid, weapon):
        (atk, dfd) = Weapons[weapon]
        self.bot.sendMessage(uid, f"{weapon}:\n攻:{atk} 防:{dfd}")

    @sending
    def stat_armor(self, uid, armor):
        (atk, dfd) = Armors[armor]
        self.bot.sendMessage(uid, f"{armor}:\n攻:{atk} 防:{dfd}")

    @sending
    def send_upgrade_limited(self, upgrade_times):
        self.bot.sendMessage(self.id, f"金幣不足 共升級{upgrade_times}次")

    @sending
    def send_upgrade_full(self, upgrade_times):
        self.bot.sendMessage(self.id, f"升級{upgrade_times}次成功")

    def _editable_send(self, content, message):
        try:
            if message == None:
                print("message is None")
            if not message:
                return self.bot.sendMessage(self.id, content)
            return message.edit_text(f"{message.text}\n{content}", timeout=15)
        except BadRequest:
            print("Bad request error")
            return message

    @sending
    def send_meet(self, name, enemy, event_name, message = None):
        return self._editable_send(f"{name}遇到了{enemy} {event_name}", message)

    @sending
    def send_fight_result(self, res, message = None):
        return self._editable_send(res, message)

    @sending
    def send_beat(self, winner, loser, coin = None, exp = None, message = None):
        content = f"{winner}打倒了{loser}"
        if coin and exp:
            content += f" ，獲得了{coin}金幣和{exp}經驗值"
        return self._editable_send(content, message)

    @sending
    def send_beaten(self, loser, winner, message = None):
        return self._editable_send(f"{loser}被{winner}打倒了 SAD", message)

    @sending
    def send_tie(self, message = None):
        return self._editable_send("竟然是百年難得一見的平手", message)

    @sending
    def send_congrats_clear(self, name, message = None):
        return self._editable_send(f"恭喜{name}通關遊戲", message)
    
    @sending
    def send_last_strike(self, name, drop_weapon_name, drop_armor_name, message = None):
        return self._editable_send(f"{name}獲得最後一擊獎勵: {drop_weapon_name}, {drop_armor_name}", message)
    
    @sending
    def send_reach_shop(self, name, message = None):
        return self._editable_send(f"{name}抵達一間商店", message)

    def chinese(self, data):
        count = 0
        for s in data:
            if ord(s) > 127:
                count += 1
        return count

    @sending
    def send_shop_items(self, goods, price, message = None):
        msg = "```\n======歡迎來到商店======\n"
        for i, (item, price) in enumerate(zip(goods,price)):
            msgstr = '{0:{wd}}'.format(item.name,wd=15-self.chinese(item.name))
            msg+= "{}. {}{:>5}\n".format(i,msgstr,price)
        msg+="```"
        if not message:
            return self.bot.sendMessage(self.id, msg, parse_mode="Markdown", reply_markup=self.end_markup)
        return message.edit_text(f"{message.text}\n{msg}", parse_mode="Markdown", reply_markup=self.end_markup)

    @sending
    def send_reach_blacksmith(self, name, message = None):
        return self._editable_send(f"{name}抵達一間鐵匠鋪", message)

    @sending
    def send_blacksmith_service(self, upgrade, weapon_cost, armor_cost, message = None):
        content = ("\n"
               f"武器升級 攻防+{upgrade} 價格:{weapon_cost}金幣\n\n"
               f"防具升級 攻防+{upgrade} 價格:{armor_cost}金幣\n"
        )
        if not message:
            return self.bot.sendMessage(self.id, content, reply_markup=self.end_markup)
        return message.edit_text(f"{message.text}\n{content}", parse_mode="Markdown", reply_markup=self.end_markup)

    @sending
    def send_find_chest(self, name, coin, weapon_name = None, message = None):
        content = f"{name}在一個寶箱裡找到了 {coin} 金幣"
        if weapon_name:
            content += f"和一個{weapon_name}"
        return self._editable_send(content, message)

    @sending
    def send_level_up(self, name, lvl, message = None):
        return self._editable_send(f"{name}升到了{lvl}級喔喔喔喔喔", message)

    @sending
    def send_not_enough_coin(self):
        self.bot.sendMessage(self.id, "金幣不足 購買失敗")

    @sending
    def send_buy_success(self):
        self.bot.sendMessage(self.id, "購買成功")

    @sending
    def send_end_game(self):
        self.bot.sendMessage(self.id, "遊戲已結束")