from OutputMean import Output
from secret import TOKEN
from typing import Dict
from telegram.ext import (Filters, Updater, Updater, CommandHandler, 
    CallbackQueryHandler, MessageHandler)
from Game import Game, stat_ids

games: Dict [int, Game] = {}

def pre_process(update, context):
    global gid, game, uid
    gid = update.message.chat_id
    if gid not in games:
        out = Output(context.bot, gid)
        games[gid] = Game(gid, out)
    game = games[gid]
    uid = update.message.from_user.id

def start(update, context):
    game.on_start()

def jizz(update, context):
    try:
        game.on_jizz(uid, int(context.args[0]))
    except:
        game.on_jizz(uid)

def map(update, context):
    game.on_map()

def pos(update, context):
    game.on_pos(uid)

def upgrade(update, context):
    args = context.args
    game.on_upgrade(uid, args[0], 1 if len(args) < 2 else args[1])

def buy(update, context):
    args = context.args
    try:
        game.on_buy(uid, int(args[0]))
    except Exception as e:
        print("ERROR:", e)
        game.out.send_wrong_argument()

def mystat(update, context):
    game.on_mystat(uid)

def end(update, context):
    game.on_end(uid)

def help(update, context):
    game.on_help()

def showpotion(update, context):
    game.on_show_potion(uid)

def drink(update, context):
    args = context.args
    try:
        game.on_drink(uid, int(args[0]))
    except:
        game.out.send_wrong_argument()

def join(update, context):
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    # if there is no username, this column will be None
    game.on_join(uid, name, username)

def change(update, context):
    game.on_change(uid)

def retire(update, context):
    game.on_retire(uid)

def showstat(update, context):
    game.on_show_stat(uid)

def handle_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    from_id = query.from_user.id
    query_data = query.data

    identifier = (chat_id, query.message.message_id)
    game = None
    if chat_id in games:
        game = games[chat_id] 
    elif chat_id in stat_ids:
        game = stat_ids[chat_id] 
    else:
        print("Game did not start")
    if game:
        game.passage(query_data.split(), from_id, identifier)
    query.answer()

updater = Updater(TOKEN)
dispatcher = updater.dispatcher
print(f"@{updater.bot.getMe().username}")

dispatcher.add_handler(MessageHandler(Filters.command, pre_process), 0)

for func in [start, jizz, map, pos, upgrade, buy, 
    mystat, end, help, showpotion, 
    drink, join, change, retire, showstat, ]:
    dispatcher.add_handler(CommandHandler(func.__name__, func), 1)
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()