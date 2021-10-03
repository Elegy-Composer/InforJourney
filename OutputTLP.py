from time import sleep
import telepot
from telepot import message_identifier
from telepot.exception import TelegramError, TooManyRequestsError, BotWasBlockedError
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from Output import Output


# def sending(func):
#     def sending_wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except TooManyRequestsError:
#             sleep(5)
#             return sending_wrapper(*args, **kwargs)
#         except (BotWasBlockedError, TelegramError):
#             #pm failed
#             #args[0] is self
#             args[0].bot.sendMessage(args[0].id, "Please add me! @inforJourneyBot")
#     return sending_wrapper

class OutputTLP(Output):
    def __init__(self, bot, id, gid):
        super().__init__(bot, id, gid) #, sending)

    def _send_message(self, *args, **kwargs):
        return self.bot.sendMessage(*args, **kwargs)

    def _edit_message_text(self, *args, message=None, identifier=None, **kwargs):
        if message:
            identifier = (message['chat']['id'], message['message_id'])
            #return message.editext(*args, **kwargs, timeout=15)
        if identifier:
            return self.bot.editMessageText(identifier, *args, **kwargs)
        else:
            raise ValueError("message or identifier should be given")
    
    def _editable_send(self, content, message):
        try:
            if message == None:
                print("message is None")
            if not message:
                return self._send_message(self.id, content)
            return self._edit_message_text(f"{message['text']}\n{content}", message=message)
        except self.BadRequest():
            print("Bad request error")
            return message

    def _send_photo(self, *args, **kwargs):
        self.bot.sendPhoto(*args, **kwargs)
        
    @staticmethod
    def gen_inline_keyboard_barkup(**kwargs):
        return InlineKeyboardMarkup(**kwargs)
    
    @staticmethod
    def gen_inline_keyboard_button(**kwargs):
        return InlineKeyboardButton(**kwargs)
    
    @staticmethod
    def BadRequest() -> type:
        return TelegramError

    @staticmethod
    def sending_decorator(func):
        def sending_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TooManyRequestsError:
                sleep(5)
                return sending_wrapper(*args, **kwargs)
            except (BotWasBlockedError, TelegramError):
                #pm failed
                #args[0] is self
                args[0].bot.sendMessage(args[0].id, "Please add me! @inforJourneyBot")
        return sending_wrapper
