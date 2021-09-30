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
            args[0]._send_message(args[0].id, "Please add me! @inforJourneyBot")
    return sending_wrapper

class Output:
    def __init__(self, bot: Bot, id):
        self.bot = bot
        self.id = id
        self.end_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Leave', callback_data='end')],
        ])
    
    def _send_message(self, *args, **kwargs):
        return self.bot.send_message(*args, **kwargs, timeout=15)

    def _edit_message_text(self, *args, message=None, identifier=None, **kwargs):
        if message:
            return message.edit_text(*args, **kwargs, timeout=15)
        elif identifier:
            return self.bot.edit_message_text(*args, **kwargs, 
                chat_id=identifier[0], message_id=identifier[1], timeout=15)
        else:
            raise ValueError("message or identifier should be given")

    @sending
    def send_help(self):
        self._send_message(self.id, helpString)

    @sending
    def send_welcome(self, name):
        self._send_message(self.id, f"{name}加入了遊戲", parse_mode="Markdown")

    @sending
    def send_start_game(self):
        self._send_message(self.id, "遊戲已開始")

    def tag_user(self, player):
        if player.username:
            return f"@{player.username}"
        else:
            return f"[{player.name}](tg://user?id={player.id})"

    @sending
    def send_player_turn_start(self, player: Player):
        self._send_message(self.id, 
            f"換{player.name}了唷 {self.tag_user(player)}\n你目前在第{player.pos}格", 
            parse_mode="Markdown"
        )
    
    @sending
    def send_jizz_result(self, player_name, jizz):
        self._send_message(self.id, f"{player_name}骰出了{jizz}.")
    
    @sending
    def send_map(self):
        self.bot.sendPhoto(self.id, open("./Img/raw_map.jpg","rb"))
    
    @sending
    def send_pos(self, name, pos):
        self._send_message(self.id, f"{name}目前在第{pos}格")

    @sending
    def send_potion(self, uid, name, potions):
        potions_str = ""
        if not potions:
            potions_str = "無"
        else:
            potions_list = [f"{i}. {str(potion)}" for i, potion in enumerate(potions)]
            potions_str = "\n".join(potions_list)
        self._send_message(uid, f"{name}的藥水們:\n{potions_str}")

    @sending
    def send_heal_result(self, player: Player, potion, heal_point):
        self._send_message(self.id, f"{player.name}飲用了{potion}\n回復{heal_point}點生命\n{player.name}現在有{player.hp}點生命")

    @sending 
    def send_wrong_argument(self):
        self._send_message(self.id, "參數錯誤")

    @sending
    def send_change(self, name, uid, avaliable_items):
        kb_list = []
        for w in avaliable_items:
            kb_list.append([InlineKeyboardButton(text=w.name, callback_data="change "+str(uid)+" "+w.name)])

        if kb_list:
            keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
            self._send_message(self.id, f"{name}, 請選擇更換裝備", reply_markup=keyboard)
        else:
            self._send_message(self.id, f"{name}沒有可更換的裝備")

    @sending 
    def change_succeed(self, name, item, identifier):
        self._edit_message_text(f"{name}已成功裝備{item}", identifier=identifier)

    @sending
    def send_retire_confirm(self, name):
        self._send_message(self.id, f"{name},你確定要退出遊戲嗎?\n確定退出請再次輸入 /retire")

    @sending
    def send_retire(self, name):
        self._send_message(self.id, f"{name}離開了遊戲")
    
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
        self._send_message(uid, "請選擇種類", reply_markup=keyboard)

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
        self._edit_message_text("請選擇種類", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_monster_stage(self, identifier):
        kb_list = []
        for i in range(4):
            kb_list.append([InlineKeyboardButton(text=f"階段{i+1}", callback_data=f"showstat monster {i}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_monsters(self, identifier, stage):
        kb_list = []
        display = list(Monsters[stage])
        for name1, name2 in zip(display[::2], display[1::2]):
            kb_list.append([
                InlineKeyboardButton(text=name1, callback_data=f"showstat monster {stage} {name1}"), 
                InlineKeyboardButton(text=name2, callback_data=f"showstat monster {stage} {name2}")
            ])
        if len(display) % 2:
            kb_list.append([InlineKeyboardButton(text=display[-1], callback_data=f"showstat monster {stage} {display[-1]}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat monster")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_bosses(self, identifier):
        kb_list = []
        for i in range(4):
            kb_list.append([InlineKeyboardButton(text=Bosses[i][0], callback_data=f"showstat boss {i}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_players(self, players, identifier):
        kb_list = []
        for player in players:
            kb_list.append([InlineKeyboardButton(text=player.name, callback_data=f"showplayer {player.id}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_items(self, identifier):
        kb_list = []
        for p in Potions:
            kb_list.append([InlineKeyboardButton(text=p, callback_data=f"showstat item {p}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_weapons(self, identifier, page):
        kb_list = []
        weapon_list = list(Weapons.items())
        if page:
            kb_list.append([InlineKeyboardButton(text="<<", callback_data=f"showstat weapon {page-1}")])

        display = weapon_list[page*6:min(page*6+6, len(weapon_list))]
        for item1, item2 in zip(display[::2], display[1::2]):
            kb_list.append([
                InlineKeyboardButton(text=item1[0], callback_data=f"showweapon {item1[0]}"),
                InlineKeyboardButton(text=item2[0], callback_data=f"showweapon {item2[0]}")
            ])
        if len(display) % 2:
            kb_list.append([InlineKeyboardButton(text=display[-1][0], callback_data=f"showweapon {display[-1][0]}")])
        if page*6 + 6 < len(weapon_list):
            kb_list.append([InlineKeyboardButton(text=">>", callback_data=f"showstat weapon {page+1}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_armors(self, identifier, page):
        kb_list = []
        armor_list = list(Armors.items())
        if page:
            kb_list.append([InlineKeyboardButton(text="<<", callback_data=f"showstat armor {page-1}")])

        display = armor_list[page*6:min(page*6+6, len(armor_list))]
        for item1, item2 in zip(display[::2], display[1::2]):
            kb_list.append([
                InlineKeyboardButton(text=item1[0], callback_data=f"showarmor {item1[0]}"),
                InlineKeyboardButton(text=item2[0], callback_data=f"showarmor {item2[0]}")
            ])
        if len(display) % 2:
            kb_list.append([InlineKeyboardButton(text=display[-1][0], callback_data=f"showarmor {display[-1][0]}")])
        if page*6 + 6 < len(armor_list):
            kb_list.append([InlineKeyboardButton(text=">>", callback_data=f"showstat armor {page+1}")])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

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

        self._send_message(uid, player_str)
    
    @sending
    def stat_monster(self, uid, monster_name, monster_data):
        self._send_message(uid, (
            f'{monster_name}: 攻:{monster_data[0]}, 防:{monster_data[1]}, HP: {monster_data[2]}\n'
            f'經驗值: {monster_data[3]}, 金幣: {monster_data[4]}\n'
            f'出現等級: {monster_data[5]} ~ {monster_data[6]}'
        ))

    @sending
    def stat_item(self, uid, potion):
        self._send_message(uid, f'恢復{"/".join(map(lambda x: str(x), potion))}點生命')

    @sending
    def stat_weapon(self, uid, weapon):
        (atk, dfd) = Weapons[weapon]
        self._send_message(uid, f"{weapon}:\n攻:{atk} 防:{dfd}")

    @sending
    def stat_armor(self, uid, armor):
        (atk, dfd) = Armors[armor]
        self._send_message(uid, f"{armor}:\n攻:{atk} 防:{dfd}")

    @sending
    def send_upgrade_limited(self, upgrade_times):
        self._send_message(self.id, f"金幣不足 共升級{upgrade_times}次")

    @sending
    def send_upgrade_full(self, upgrade_times):
        self._send_message(self.id, f"升級{upgrade_times}次成功")

    def _editable_send(self, content, message):
        try:
            if message == None:
                print("message is None")
            if not message:
                return self._send_message(self.id, content)
            return self._edit_message_text(f"{message.text}\n{content}", message=message)
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
            return self._send_message(self.id, msg, parse_mode="Markdown", reply_markup=self.end_markup)
        return self._edit_message_text(f"{message.text}\n{msg}", message=message, parse_mode="Markdown", reply_markup=self.end_markup)

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
            return self._send_message(self.id, content, reply_markup=self.end_markup)
        return self._edit_message_text(f"{message.text}\n{content}", message=message, parse_mode="Markdown", reply_markup=self.end_markup)

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
        self._send_message(self.id, "金幣不足 購買失敗")

    @sending
    def send_buy_success(self):
        self._send_message(self.id, "購買成功")

    @sending
    def send_end_game(self):
        self._send_message(self.id, "遊戲已結束")

    def direct_from_in(self, game, query_data, uid, identifier):
        try:
            if query_data[0] == "change" and len(query_data) > 2:
                if uid == int(query_data[1]):
                    game.request_change(uid, query_data[2], identifier)
                else:
                    print(uid, query_data)
            elif query_data[0] == "end":
                game.request_end(uid)
            elif query_data[0] == "showstat":
                try:
                    if len(query_data) > 3:
                        if query_data[1] == "monster":
                            game.show_monster(uid, query_data[3], Monsters[int(query_data[2])][query_data[3]])
                    if len(query_data) > 2:
                        if query_data[1] == "monster":
                            i = int(query_data[2])
                            self.stat_monsters(identifier, i)
                        elif query_data[1] == "weapon":
                            start = int(query_data[2])
                            self.stat_weapons(identifier, start)
                        elif query_data[1] == "armor":
                            start = int(query_data[2])
                            self.stat_armors(identifier, start)
                        elif query_data[1] == "boss":
                            i = int(query_data[2])
                            game.show_monster(uid, Bosses[i][0], Bosses[i][1:])
                        elif query_data[1] == "item":
                            if query_data[2] in Potions:
                                potion = Potions[query_data[2]]
                                self.stat_item(uid, potion)
                    elif len(query_data) > 1:
                        if query_data[1] == "player":
                            self.stat_players(game.get_players(), identifier)
                        elif query_data[1] == "boss":
                            self.stat_bosses(identifier)
                        elif query_data[1] == "item":
                            self.stat_items(identifier)
                        elif query_data[1] == "monster":
                            self.stat_monster_stage(identifier)
                    else:
                        self.stat_category(identifier)
                except:
                    pass
            elif query_data[0] == "showplayer" and len(query_data)>1:
                try:
                    show_player_id = int(query_data[1])
                    game.request_show_player(uid, show_player_id)
                except:
                    pass
            elif query_data[0] == "showweapon" and len(query_data)>1:
                self.stat_weapon(uid, query_data[1])
            elif query_data[0] == "showarmor" and len(query_data)>1:
                self.stat_armor(uid, query_data[1])
        except:
            pass