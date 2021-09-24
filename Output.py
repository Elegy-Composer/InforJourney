from Player import Player
from Data import Potions, Bosses, Exps
from time import sleep
import telepot
from telepot.exception import TooManyRequestsError, BotWasBlockedError
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

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
            func(*args, **kwargs)
        except TooManyRequestsError:
            sleep(5)
            func(*args, **kwargs)
    return sending_wrapper

def identifier(msg):
    chat_id = msg['chat']['id']
    identifier = (chat_id, msg['message_id'])
    return identifier

class Output:
    def __init__(self, bot: telepot.Bot, id):
        self.bot = bot
        self.id = id
        self.change_msg = None
        self.stat_msg = None
    
    @sending
    def send_help(self):
        self.bot.sendMessage(self.id, helpString)

    @sending
    def send_welcome(self, name):
        self.bot.sendMessage(self.id, f"{name}加入了遊戲", parse_mode="Markdown")
    
    @sending
    def send_map(self):
        self.bot.sendPhoto(self.id, open("./Img/raw_map.jpg","rb"))
    
    @sending
    def send_pos(self, name, pos):
        self.bot.sendMessage(self.id, f"{name}目前在第{pos}格")

    @sending
    def send_potion(self, name, potions):
        potions_str = ""
        if not potions:
            potions_str = "無"
        else:
            potions_list = [f"{i}. {str(potion)}" for i, potion in enumerate(potions)]
            potions_str = "\n".join(potions_list)
        self.bot.sendMessage(self.id, f"{name}的藥水們:\n{potions_str}")

    @sending
    def send_change(self, name, uid, avaliable_items):
        kb_list = []
        for w in avaliable_items:
            kb_list.append([InlineKeyboardButton(text=w.name, callback_data="change "+str(uid)+" "+w.name)])

        if kb_list:
            keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
            msg = self.bot.sendMessage(self.id, f"{name}, 請選擇更換裝備", reply_markup=keyboard)
            self.change_msg = msg
        else:
            self.bot.sendMessage(self.id, f"{name}沒有可更換的裝備")

    @sending 
    def change_succeed(self, name, item):
        if self.change_msg:
            self.bot.editMessageText(identifier(self.change_msg), f"{name}已成功裝備{item}")
            self.change_msg = None
        else:
            print("self.change_msg is None, should not happen")
            print(f"name: {name}\nitem: {item}")
            raise ValueError("chanege_msg is None.\nBe sure to call send_change first.")

    @sending
    def send_retire_confirm(self, name):
        self.bot.sendMessage(self.id, f"{name},你確定要退出遊戲嗎?\n確定退出請再次輸入 /retire")

    @sending
    def send_retire(self, name):
        self.bot.sendMessage(self.id, f"{name}離開了遊戲")
    
    @sending
    def send_stat(self, uid):
        try: 
            kb_list = [
                [InlineKeyboardButton(text="小怪", callback_data="showstat monster"),
                InlineKeyboardButton(text="首領", callback_data="showstat boss")],
                [InlineKeyboardButton(text="玩家", callback_data="showstat player"),
                InlineKeyboardButton(text="武器", callback_data="showstat weapon 0")],
                [InlineKeyboardButton(text="防具", callback_data="showstat armor 0"),
                InlineKeyboardButton(text="道具", callback_data="showstat item")]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
            msg = self.bot.sendMessage(uid, "請選擇種類", reply_markup=keyboard)
            self.stat_msg = msg
        except BotWasBlockedError as e:
            print("err")
            print(e)
            self.bot.sendMessage(self.id, "Please add me! @inforJourneyBot")

    @sending
    def stat_category(self):
        kb_list = [
            [InlineKeyboardButton(text="小怪", callback_data="showstat monster"),
            InlineKeyboardButton(text="首領", callback_data="showstat boss")],
            [InlineKeyboardButton(text="玩家", callback_data="showstat player"),
            InlineKeyboardButton(text="武器", callback_data="showstat weapon 0")],
            [InlineKeyboardButton(text="防具", callback_data="showstat armor 0"),
            InlineKeyboardButton(text="道具", callback_data="showstat item")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText(identifier(self.stat_msg), "請選擇種類", reply_markup=keyboard)

    @sending
    def stat_monster_stage(self):
        kb_list = []
        for i in range(4):
            kb_list.append([InlineKeyboardButton(text="階段"+str(i+1), callback_data="showstat monster "+str(i))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText(identifier(self.stat_msg), "請選擇", reply_markup=keyboard)

    @sending
    def stat_bosses(self):
        kb_list = []
        for i in range(4):
            kb_list.append([InlineKeyboardButton(text=Bosses[i][0], callback_data="showstat boss "+str(i))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText(identifier(self.stat_msg), "請選擇", reply_markup=keyboard)

    @sending
    def stat_players(self, players):
        kb_list = []
        for player in players:
            kb_list.append([InlineKeyboardButton(text=player.name, callback_data="showplayer "+str(player.id))])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText(identifier(self.stat_msg), "請選擇", reply_markup=keyboard)

    @sending
    def stat_items(self):
        kb_list = []
        for p in Potions:
            kb_list.append([InlineKeyboardButton(text=p, callback_data="showstat item "+p)])
        kb_list.append([InlineKeyboardButton(text="上一層", callback_data="showstat")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
        self.bot.editMessageText(identifier(self.stat_msg), "請選擇", reply_markup=keyboard)

    @sending
    def stat_player(self, player: Player):
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

        self.bot.sendMessage(self.id, player_str)
    
    @sending
    def stat_monster(self, monster_name, monster_data):
        self.bot.sendMessage(self.id, (
            f'{monster_name}: 攻:{monster_data[0]}, 防:{monster_data[1]}, HP: {monster_data[2]}\n'
            f'經驗值: {monster_data[3]}, 金幣: {monster_data[4]}\n'
            f'出現等級: {monster_data[5]} ~ {monster_data[6]}'
        ))

    @sending
    def stat_item(self, potion):
        self.bot.sendMessage(self.id, "恢復"+"/".join(map(lambda x: str(x), potion))+"點生命")