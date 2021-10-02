
from Player import Player
from secret import TOKEN
from Output import Output
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, RetryAfter, TimedOut, Unauthorized
from time import sleep


def sending(func):
    def sending_wrapper(*args, **kwargs):
        try:
            print(f"running {func.__name__} in decorator")
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

class OutputPTB(Output):
    def __init__(self, bot, id, gid):
        super().__init__(bot, id, gid, sending)

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
    
    def _send_photo(self, *args, **kwargs):
        self.bot.send_photo(*args, **kwargs)
    
    def _editable_send(self, content, message):
        try:
            if message == None:
                print("message is None")
            if not message:
                return self._send_message(self.id, content)
            return self._edit_message_text(f"{message.text}\n{content}", message=message)
        except self.BadRequest():
            print("Bad request error")
            return message
        
    @staticmethod
    def gen_inline_keyboard_markup(**kwargs):
        return InlineKeyboardMarkup(**kwargs)
    
    @staticmethod
    def gen_inline_keyboard_button(**kwargs):
        return InlineKeyboardButton(**kwargs)
    
    @staticmethod
    def BadRequest() -> type:
        return BadRequest

