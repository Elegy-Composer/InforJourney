# all mighty miohitokiri
import telegram
from OutputMean import Output
from urllib3.poolmanager import PoolKey
from Events import EventCanEnd
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from num2words import num2words
from random import randint
from enum import Enum
from pprint import pprint
from urllib3.util.request import make_headers
from typing import Dict
import threading

from urllib3.util.url import PERCENT_RE

from Player import Player
from Map import GenMap
from Data import Armors, Pending, Exps, Monsters, Bosses, Potions, Weapons
from Entity import Monster, Boss
from secret import TOKEN

max_num = 4
false = False
true = True
bot = telepot.Bot(TOKEN)
games = {}
weapon_list = list(Weapons.items())
armor_list = list(Armors.items())
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

def isTrue(str, none = False):
    if str is None:
        return none
    if not str:
        return False
    if str == -1:
        return False
    if str.lower() in ["false","0","no","nay","nah"]:
        return False
    return True

def handle(msg):
    pprint(msg)
    if "text" not in msg or msg["text"][0] != '/':
        return
    gid = msg["chat"]["id"]
    if gid not in games:
        bot_mean = telegram.Bot(TOKEN)
        out = Output(bot_mean, gid)
        games[gid] = Game(gid, out)
    in_data = msg["text"].replace("@inforJourneyBot", "").split()
    if "username" in msg["from"]:
        username = msg["from"]["username"]
    else:
        username = None
    games[gid].on_msg(in_data[0][1:], in_data[1:], msg["from"]["id"], msg["from"]["first_name"], username)

def handle_callback(msg):
    chat_id = msg['message']['chat']['id']
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    identifier = (chat_id, msg['message']['message_id'])
    if chat_id in games:
        games[chat_id].on_callback(query_data, from_id, identifier)
    elif chat_id in stat_ids:
        stat_ids[chat_id].on_callback(query_data, from_id, identifier)
    else:
        print("Game did not start")
    bot.answerCallbackQuery(query_id)

def tag_user(player):
    if player.username:
        return f"@{player.username}"
    else:
        return f"[{player.name}](tg://user?id={player.id})"

class State(Enum):
    UNSTARTED = 0
    STARTED = 1
    PENDING = 2
    EVENT = 3
    END = 4
    ERROR = -1


class Game:
    def __init__(self, groupid, out: Output):
        self.Map = GenMap()
        self.id = groupid
        self.ids = {}
        self.players = []
        self.state = State.UNSTARTED
        self.now_player_no = -1
        self.out = out

    def now_player(self):
        return self.players[self.now_player_no]

    def on_msg(self, msg, args, uid, name, username):
        print(args)
        try:
            {
                "start": (lambda x:
                    self.start()
                        ),
                "map": (lambda x:
                    x or  # unless
                        self.out.send_map()
                      ),
                "pos": (lambda x:
                    x or 
                        self.out.send_pos(self.ids[uid].name, self.ids[uid].pos)
                      ),
                "jizz": (lambda x:
                    self.state != State.PENDING or self.now_player().id != uid or # unless
                        self.move(self.now_player(), args)
                       ),
                "upgrade": (lambda x:
                    self.state != State.EVENT or self.now_player().id != uid or # unless
                        self.now_player().pending != Pending.BLACKSMITH or
                            self.now_player().upgrade(args[0], self.out, 1 if len(args) < 2 else args[1])
                           ),
                "buy": (lambda x:
                    self.state != State.EVENT or self.now_player().id != uid or # unless
                        self.now_player().pending != Pending.SHOP or
                            self.now_player().purchase(int(args[0]),self.out)
                           ),
                "mystat": (lambda x:
                    x or self.show_player(uid, self.ids[uid])
                            ),
                "end": (lambda x:
                    self.state != State.EVENT or self.now_player().id != uid or
                        self.now_player().pending == Pending.CHANGE or
                        self.end()
                       ),
                "help": (lambda x:
                    x or 
                        self.out.send_help()
                      ),
                "showpotion": (lambda x:
                    x or 
                        self.out.send_potion(uid, self.ids[uid].name, self.ids[uid].potions)
                      ),
                "drink": (lambda x:
                    self.state != State.PENDING or self.now_player().id != uid or # unless
                        self.drink(self.now_player(), args)
                      ),
            }[msg](self.state == State.UNSTARTED)
        except KeyError:
            if msg == "join":
                if self.state == State.UNSTARTED:
                    if uid not in self.ids:
                        self.players.append(Player(uid, name, username))
                        self.ids.update({uid : self.players[-1]})
                        self.out.send_welcome(name)
                        if len(self.players) == 4:
                            self.start()
                else:
                    if len(self.players) < 4 and uid not in self.ids:
                        self.players.append(Player(uid, name, username))
                        self.ids.update({uid : self.players[-1]})
                        self.out.send_welcome(name)
                return
            if(self.state != State.UNSTARTED):
                if msg == "change":
                    self.out.send_change(self.ids[uid].name, uid, self.ids[uid].unused_weapons + self.ids[uid].unused_armors)
                elif msg == "retire":
                    if self.ids[uid].pending != Pending.RETIRE:
                        self.out.send_retire_confirm(self.ids[uid].name)
                        self.ids[uid].pending = Pending.RETIRE
                    else:
                        self.out.send_retire(self.ids[uid].name)
                        idx = self.players.index(self.ids[uid])
                        self.players.pop(idx)
                        del self.ids[uid]
                        if len(self.players) == 0:
                            self.endgame()
                            return
                        if idx < self.now_player_no:
                            self.now_player_no -= 1
                        elif idx == self.now_player_no:
                            self.next_player()
                elif msg == "showstat":
                    self.out.send_stat(uid)
                    stat_ids[uid] = self
    def on_callback(self, query_data, uid, identifier):
        print("on callback\nquery_data: {}\nuid: {}\nidentifier: {}\n".format(query_data, uid, identifier))
        query_data = query_data.split()
        try:
            if query_data[0] == "change" and len(query_data) > 2:
                if uid == int(query_data[1]):
                    changed = self.ids[uid].change2(query_data[2])
                    if changed:
                        print("change called")
                        self.out.change_succeed(self.ids[uid].name, changed, identifier)
                else:
                    print(uid, query_data)
            elif query_data[0] == "end":
                if self.state == State.EVENT and self.now_player().id == uid:
                    self.end()
            elif query_data[0] == "showstat":
                try:
                    if len(query_data) > 3:
                        if query_data[1] == "monster":
                            self.show_monster(uid, query_data[3], Monsters[int(query_data[2])][query_data[3]])
                    if len(query_data) > 2:
                        if query_data[1] == "monster":
                            i = int(query_data[2])
                            self.out.stat_monsters(identifier, i)
                        elif query_data[1] == "weapon":
                            start = int(query_data[2])
                            self.out.stat_weapons(identifier, start)
                        elif query_data[1] == "armor":
                            start = int(query_data[2])
                            self.out.stat_armors(identifier, start)
                        elif query_data[1] == "boss":
                            i = int(query_data[2])
                            self.show_monster(uid, Bosses[i][0], Bosses[i][1:])
                        elif query_data[1] == "item":
                            if query_data[2] in Potions:
                                potion = Potions[query_data[2]]
                                self.out.stat_item(uid, potion)
                    elif len(query_data) > 1:
                        if query_data[1] == "player":
                            self.out.stat_players(self.players, identifier)
                        elif query_data[1] == "boss":
                            self.out.stat_bosses(identifier)
                        elif query_data[1] == "item":
                            self.out.stat_items(identifier)
                        elif query_data[1] == "monster":
                            self.out.stat_monster_stage(identifier)
                    else:
                        self.out.stat_category(identifier)
                except:
                    pass
            elif query_data[0] == "showplayer" and len(query_data)>1:
                try:
                    show_player_id = int(query_data[1])
                    self.show_player(uid, self.ids[show_player_id])
                except:
                    pass
            elif query_data[0] == "showweapon" and len(query_data)>1:
                self.out.stat_weapon(uid, query_data[1])
            elif query_data[0] == "showarmor" and len(query_data)>1:
                self.out.stat_armor(uid, query_data[1])
        except:
            pass
    def show_player(self, uid, entity):
        print('showing')
        print(entity)
        self.out.stat_player(uid, entity)
    def show_monster(self, uid, name, monster_data):
        self.out.stat_monster(uid, name, monster_data)
    def start(self):
        if self.state != State.UNSTARTED:
            return
        if len(self.players) == 0:
            return
        self.state = State.STARTED
        self.out.send_start_game()
        self.next_player() 
    def end(self):
        sleep(2) # sleep 3 sec for reduce loding
        self.now_player().on_hand.clear()
        self.next_player()
    
    def next_player(self):
        self.now_player_no = (self.now_player_no + 1) % len(self.players)
        self.state = State.PENDING
        self.out.send_player_turn_start(self.now_player())
    
    def move(self, player, args):
        self.state = State.EVENT
        try:
            moved = int(args[0])
        except:
            moved = randint(1, 4)
        self.out.send_jizz_result(player.name, num2words(moved))
        player.move(moved)
        for other_player in self.players:
            if other_player is not player:
                if other_player.pos == player.pos:
                    player.meet(other_player, self.out)
        if self.Map[player.pos] is not None:
            meet = player.meet(self.Map[player.pos], self.out, True)
            if isinstance(meet, str):
                self.endgame()
            elif meet:
                self.end()
        else:
            self.end()
    def drink(self, player, args):
        try:
            i = int(args[0])
            self.out.send_heal_result(player, player.potions[i], player.potions[i].drink(player))
            player.potions.pop(i)
        except:
            self.out.send_wrong_argument()
    def endgame(self):
        self.out.send_end_game()
        game_stat_ids = [k for k,v in stat_ids.items() if v == self]
        for k in game_stat_ids:
            del stat_ids[k]
        self.__init__(self.id, self.out)


stat_ids: Dict[int, Game] = dict()


loop = MessageLoop(bot, {'chat': handle,
                  'callback_query': handle_callback}
).run_as_thread()

# Keep the program running.
while 1:
    sleep(10)