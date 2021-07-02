# all mighty miohitokiri
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

from urllib3.util.url import PERCENT_RE

from Player import Player
from Map import GenMap
from Data import Pending, Exps, Monsters, Bosses
from Entity import Monster, Boss
from secret import TOKEN

max_num = 4
false = False
true = True
bot = telepot.Bot(TOKEN)
games = {}
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
coin - SHow your coins
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
        games[gid] = Game(gid)
    in_data = msg["text"].replace("@inforJourneyBot", "").split()
    games[gid].on_msg(in_data[0][1:], in_data[1:], msg["from"]["id"], msg["from"]["first_name"])

def handle_callback(msg):
    chat_id = msg['message']['chat']['id']
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    identifier = (chat_id, msg['message']['message_id'])
    if chat_id in games:
        games[chat_id].on_callback(query_data, from_id, identifier)
    else:
        print("Game did not start")
    #bot.sendMessage(from_id, "已成功裝備" + query_data + "")
    bot.answerCallbackQuery(query_id)


class State(Enum):
    UNSTARTED = 0
    STARTED = 1
    PENDING = 2
    EVENT = 3
    END = 4
    ERROR = -1


class Game:
    def __init__(self, groupid):
        self.Map = GenMap()
        self.id = groupid
        self.ids = {}
        self.players = []
        self.state = State.UNSTARTED
        self.now_player_no = -1

    def say(self, msg, parse=None, edit=False, markup=None):

        print(msg)
        try:
            if edit:
                edited = telepot.message_identifier(edit)
                ret = bot.editMessageText(edited, edit['text'] + '\n' + msg, parse_mode=parse, reply_markup=markup)
            else:
                ret = bot.sendMessage(self.id, msg, parse_mode = parse, reply_markup=markup)
        except telepot.exception.TooManyRequestsError:
            sleep(5)
            ret = self.say(msg, parse, edit, markup)
        sleep(0.5) # sleep 1 sec for every say
        return ret
    def now_player(self):
        return self.players[self.now_player_no]

    def on_msg(self, msg, args, uid, name):
        print(args)
        try:
            {
                "join": (lambda x:
                    not x or (uid in self.ids) or  # unless
                        self.players.append(Player(uid, name)) and 0 or
                        self.ids.update({uid : self.players[-1]}) and 0 or
                        self.say("{}加入了遊戲".format(name),"Markdown") and 0 or
                        len(self.players) != 4 or  # unless
                            self.start()
                       ),
                "start": (lambda x:
                    self.start()
                        ),
                "map": (lambda x:
                    x or  # unless
                        bot.sendPhoto(self.id,open("./Img/raw_map.jpg","rb"))
                      ),
                "pos": (lambda x:
                    x or self.say("{}目前在第{}格".format(self.ids[uid].name,self.ids[uid].pos))
                      ),
                "jizz": (lambda x:
                    self.state != State.PENDING or self.now_player().id != uid or # unless
                        self.move(self.now_player(), args)
                       ),
                "upgrade": (lambda x:
                    self.state != State.EVENT or self.now_player().id != uid or # unless
                        self.now_player().pending != Pending.BLACKSMITH or
                            self.now_player().upgrade(args[0],self.say, 1 if len(args) < 2 else args[1])
                           ),
                "buy": (lambda x:
                    self.state != State.EVENT or self.now_player().id != uid or # unless
                        self.now_player().pending != Pending.SHOP or
                            self.now_player().purchase(int(args[0]),self.say)
                           ),
                "mystat": (lambda x:
                    x or self.mystat(self.ids[uid])
                            ),
                "end": (lambda x:
                    self.state != State.EVENT or self.now_player().id != uid or
                        self.now_player().pending == Pending.CHANGE or
                        self.end()
                       ),
                "exp": (lambda x:
                    x or self.say("{}目前經驗值：{}\n升級所需經驗值：{}".format(self.ids[uid].name, self.ids[uid].exp, Exps[self.ids[uid].lvl]))
                      ),
                "coin": (lambda x:
                    x or self.say("{}現在有 {} 金幣".format(self.ids[uid].name, self.ids[uid].coin))
                      ),
                "help": (lambda x:
                    x or self.say(helpString)
                      ),
                "showpotion": (lambda x:
                    x or self.say("{}的藥水們:\n{}".format(self.ids[uid].name, "無" if self.ids[uid].potions == [] else "\n".join([str(i)+". "+str(potion) for i, potion in enumerate(self.ids[uid].potions)])))
                      ),
                "drink": (lambda x:
                    self.state != State.PENDING or self.now_player().id != uid or # unless
                        self.drink(self.now_player(), args)
                      ),
            }[msg](self.state == State.UNSTARTED)
        except KeyError:
            if(self.state != State.UNSTARTED):
                if msg == "change":
                    kb_list = []
                    for w in self.ids[uid].unused_weapons:
                        kb_list.append([InlineKeyboardButton(text=w.name, callback_data="change "+str(uid)+" "+w.name)])
                    for w in self.ids[uid].unused_armors:
                        kb_list.append([InlineKeyboardButton(text=w.name, callback_data="change "+str(uid)+" "+w.name)])
                    #kb_list.append([InlineKeyboardButton(text="星爆氣流斬", callback_data="change 星爆氣流斬")])
                    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
                    bot.sendMessage(self.id, "{}, 請選擇更換裝備".format(self.ids[uid].name), reply_markup=keyboard)
                elif msg == "retire":
                    if self.ids[uid].pending != Pending.RETIRE:
                        self.say("{},你確定要退出遊戲嗎?\n確定退出請再次輸入 /retire".format(self.ids[uid].name))
                        self.ids[uid].pending = Pending.RETIRE
                    else:
                        self.say("{}離開了遊戲".format(self.ids[uid].name))
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
                    kb_list = [
                        [InlineKeyboardButton(text="小怪", callback_data="showstat monster")],
                        [InlineKeyboardButton(text="首領", callback_data="showstat boss")],
                        [InlineKeyboardButton(text="玩家", callback_data="showstat player")]
                    ]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
                    bot.sendMessage(self.id, "請選擇種類", reply_markup=keyboard)
    def on_callback(self, query_data, uid, identifier):
        query_data = query_data.split()
        try:
            if query_data[0] == "change" and len(query_data) > 2:
                if uid == int(query_data[1]):
                    changed = self.ids[uid].change2(query_data[2])
                    if changed:
                        bot.editMessageText(identifier, "{}已成功裝備{}".format(self.ids[uid].name, changed))
                else:
                    print(uid, query_data)
            elif query_data[0] == "end":
                if self.state == State.EVENT and self.now_player().id == uid:
                    self.end()
            elif query_data[0] == "showstat":
                try:
                    if len(query_data) > 3:
                        self.show_monster(query_data[3], Monsters[int(query_data[2])][query_data[3]])
                    if len(query_data) > 2:
                        kb_list = []
                        if query_data[1] == "monster":
                            i = int(query_data[2])
                            for name in Monsters[i]:
                                kb_list.append([InlineKeyboardButton(text=name, callback_data="showstat monster "+query_data[2]+" "+name)])
                            kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat monster")])
                            keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
                            bot.editMessageText(identifier, "請選擇", reply_markup=keyboard)
                        else:
                            i = int(query_data[2])
                            self.show_monster(Bosses[i][0], Bosses[i][1:])
                    elif len(query_data) > 1:
                        kb_list = []
                        if query_data[1] == "player":
                            for player in self.players:
                                kb_list.append([InlineKeyboardButton(text=player.name, callback_data="showplayer "+str(player.id))])
                        elif query_data[1] == "monster":
                            for i in range(4):
                                kb_list.append([InlineKeyboardButton(text="階段"+str(i+1), callback_data="showstat monster "+str(i))])
                        else:
                            for i in range(4):
                                kb_list.append([InlineKeyboardButton(text=Bosses[i][0], callback_data="showstat boss "+str(i))])
                        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
                        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
                        bot.editMessageText(identifier, "請選擇", reply_markup=keyboard)
                    else:
                        kb_list = [
                            [InlineKeyboardButton(text="小怪", callback_data="showstat monster")],
                            [InlineKeyboardButton(text="首領", callback_data="showstat boss")],
                            [InlineKeyboardButton(text="玩家", callback_data="showstat player")]
                        ]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
                        bot.editMessageText(identifier, "請選擇種類", reply_markup=keyboard)
                except:
                    pass
            elif query_data[0] == "showplayer" and len(query_data)>1:
                try:
                    show_player_id = int(query_data[1])
                    self.show_player(self.ids[show_player_id])
                except:
                    pass
        except:
            pass
    def show_player(self, entity):
        self.say("{}: 等級 {}\n攻:{}, 防:{}, \nHP: {}, 最大HP: {}\n 武器:{}\n攻+{} 防+{}\n 防具:{}\n攻+{} 防+{}".format(entity.name, entity.lvl, entity.atk, entity.dfd, entity.hp, entity.maxhp, entity.weapon.name, entity.weapon.atk, entity.weapon.dfd, entity.armor.name, entity.armor.atk, entity.armor.dfd))
    def show_monster(self, name, monster_data):
        self.say("{}: 攻:{}, 防:{}, HP: {}\n經驗值: {}, 金幣: {}\n出現等級: {} ~ {}".format(
            name, monster_data[0], 
            monster_data[1], monster_data[2], monster_data[3], 
            monster_data[4], monster_data[5], monster_data[6]))
    def mystat(self, entity):
        self.say("{}: 等級 {}\n攻:{}, 防:{}, \nHP: {}, 最大HP: {}\n 武器:{}\n攻+{} 防+{}\n 防具:{}\n攻+{} 防+{}".format(entity.name, entity.lvl, entity.atk, entity.dfd, entity.hp, entity.maxhp, entity.weapon.name, entity.weapon.atk, entity.weapon.dfd, entity.armor.name, entity.armor.atk, entity.armor.dfd))
    def start(self):
        if self.state != State.UNSTARTED:
            return
        if len(self.players) == 0:
            return
        self.state = State.STARTED
        self.say("遊戲已開始")
        self.next_player() 
    def end(self):
        sleep(2) # sleep 3 sec for reduce loding
        self.now_player().on_hand.clear()
        self.next_player()
    
    def next_player(self):
        self.now_player_no = (self.now_player_no + 1) % len(self.players)
        self.state = State.PENDING
        self.say("換{}了唷\n你目前在第{}格".format(self.now_player().name, self.now_player().pos))
    
    def move(self, player, args):
        self.state = State.EVENT
        try:
            moved = int(args[0])
        except:
            moved = randint(1, 4)
        self.say("{}骰出了{}.".format(player.name, num2words(moved)))
        player.move(moved)
        for other_player in self.players:
            if other_player is not player:
                if other_player.pos == player.pos:
                    player.meet(other_player, self.say)
        if self.Map[player.pos] is not None:
            meet = player.meet(self.Map[player.pos], self.say, True)
            if isinstance(meet, str):
                self.endgame()
            elif meet:
                self.end()
        else:
            self.end()
    def drink(self, player, args):
        try:
            i = int(args[0])
            self.say("{0}飲用了{1}\n回復{2}點生命\n{0}現在有{3}點生命".format(player.name, player.potions[i], player.potions[i].drink(player), player.hp))
            player.potions.pop(i)
        except:
            self.say("參數錯誤")
    def endgame(self):
        self.say("遊戲已結束")
        self.__init__(self.id)


MessageLoop(bot, {'chat': handle,
                  'callback_query': handle_callback}
).run_as_thread()

# Keep the program running.
while 1:
    sleep(10)