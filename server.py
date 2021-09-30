# all mighty miohitokiri
# from os import stat
# from re import UNICODE
import telegram
from OutputMean import Output
# from urllib3.poolmanager import PoolKey
# from Events import EventCanEnd
import telepot
from telepot.loop import MessageLoop
# from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
# from num2words import num2words
# from random import randint
# from enum import Enum
from pprint import pprint
# from urllib3.util.request import make_headers
# from typing import Dict
# import threading

# from urllib3.util.url import PERCENT_RE

# from Player import Player
# from Map import GenMap
from Data import Armors, Weapons #Pending, Exps, Monsters, Bosses, Potions, Weapons
# from Entity import Monster, Boss
from secret import TOKEN
from Game import Game, stat_ids

max_num = 4
false = False
true = True
bot = telepot.Bot(TOKEN)
games = {}
weapon_list = list(Weapons.items())
armor_list = list(Armors.items())
# helpString = """join - Join a game
# start - Start a game
# jizz - Throw a die to move
# map - Show the game map
# pos - Show Your positon
# buy - [no] Buy an item in shop
# upgrade - [weapon/armor] Upgrade weapon or armor in blacksmith shop
# change - Change weapon or armor
# end - Leave shop or blacksmith shop
# drink - [no] Drink a potion
# mystat - Show your status
# showpotion - Show all your potions
# showstat - Show status of chosen entity
# retire - retire from game
# exp - Show your exp
# coin - Show your coins
# help - Show game help"""

# def isTrue(str, none = False):
#     if str is None:
#         return none
#     if not str:
#         return False
#     if str == -1:
#         return False
#     if str.lower() in ["false","0","no","nay","nah"]:
#         return False
#     return True

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
    # games[gid].on_msg(in_data[0][1:], in_data[1:], msg["from"]["id"], msg["from"]["first_name"], username)
    dispatch_msg(gid, in_data[0][1:], in_data[1:], msg["from"]["id"], msg["from"]["first_name"], username)

def dispatch_msg(gid, msg, args, uid, name, username):
    game = games[gid]
    if msg == "start":
        game.on_start()
    elif msg == "map":
        game.on_map()
    elif msg == "pos":
        game.on_pos(uid)
    elif msg == "jizz":
        try:
            game.on_jizz(uid, int(args[0]))
        except:
            game.on_jizz(uid)
    elif msg == "upgrade":
        game.on_upgrade(uid, args[0], 1 if len(args) < 2 else args[1])
    elif msg == "buy":
        try:
            game.on_buy(uid, int(args[0]))
        except:
            game.out.send_wrong_argument()
    elif msg == "mystat":
        game.on_mystat(uid)
    elif msg == "end":
        game.on_end(uid)
    elif msg == "help":
        game.on_help()
    elif msg == "showpotion":
        game.on_show_potion(uid)
    elif msg == "drink":
        try:
            game.on_drink(uid, int(args[0]))
        except:
            game.out.send_wrong_argument()
    elif msg == "join":
        game.on_join(uid, name, username)
    elif msg == "change":
        game.on_change(uid)
    elif msg == "retire":
        game.on_retire(uid)
    elif msg == "showstat":
        game.on_show_stat(uid)

def handle_callback(msg):
    chat_id = msg['message']['chat']['id']
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    identifier = (chat_id, msg['message']['message_id'])
    game = None
    if chat_id in games:
        game = games[chat_id] #.on_callback(query_data.split(), from_id, identifier)
    elif chat_id in stat_ids:
        game = stat_ids[chat_id] #.on_callback(query_data.split(), from_id, identifier)
    else:
        print("Game did not start")
    if game:
        game.passage(query_data.split(), from_id, identifier)
    bot.answerCallbackQuery(query_id)

# def tag_user(player):
#     if player.username:
#         return f"@{player.username}"
#     else:
#         return f"[{player.name}](tg://user?id={player.id})"


loop = MessageLoop(bot, {'chat': handle,
                  'callback_query': handle_callback}
).run_as_thread()

# Keep the program running.
while 1:
    sleep(10)