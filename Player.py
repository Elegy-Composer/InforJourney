from logging import makeLogRecord
from Entity import Boss, Entity, Monster
from Data import Bosses, Positions
from Gen import Gen
from Events import Chest, Shop, Blacksmith
from Data import Pending, Exps, LevelUp
from Item import Weapon, Armor, Item
from pprint import pprint
from collections import deque
# from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# EndMarkup = InlineKeyboardMarkup(inline_keyboard=[
#                    [InlineKeyboardButton(text='Leave', callback_data='end')],
#                ])

def chinese(data):
    count = 0
    for s in data:
        if ord(s) > 127:
            count += 1
    return count

class Player(Entity):
    def __init__(self, uid, name, username):
        super(Player, self).__init__(name, 30, 10, 5) # hp, at, dfd
        self.username = username
        self.id = uid
        self.exp = 0
        self.maxhp = 30
        self.lvl = 1
        self.coin = 10
        self.pos = 0
        self.weapon = Weapon("短刀")
        self.armor = Armor("皮衣")
        self.on_hand = deque() # to change 
        self.potions = []
        self.unused_weapons = []
        self.unused_armors = []
        self.pending = Pending.NONE
    def phase(self):
        return (self.pos-1)//10 if self.pos else 0
    def move(self, move):
        while move:
            move -= 1
            self.pos += 1
            if self.pos in Positions["Boss"]:
                break
    #def recieve(self)

    def entity_type(self):
        return "玩家"

    def meet(self, event, out, first_time=False):
        print("meet")
        return event.invoke_event(self, out, first_time)

    # not in use
    # def ask_change(self,item,say):
    #     self.on_hand.appendleft(item)
    #     if isinstance(item, Weapon):
    #         say("{}，你已獲得新武器：\n{}\n 攻+{} 防+{}\n是否將其替換舊有武器\n{}\n 攻+{} 防+{}".format(self.name, item.name, item.atk, item.dfd, self.weapon.name, self.weapon.atk, self.weapon.dfd))
    #     else:
    #         say("{}，你已獲得新防具：\n{}\n 攻+{} 防+{}\n是否將其替換舊有防具\n{}\n 攻+{} 防+{}".format(self.name, item.name, item.atk, item.dfd, self.armor.name, self.armor.atk, self.armor.dfd))
    #     self.pending = Pending.CHANGE

    # not in use
    # def change(self, change, say):
    #     pprint(self.on_hand)
    #     assert(isinstance(self.on_hand[0],Item))
    #     if change:
    #         say("{}已成功裝備{}".format(self.name,self.on_hand[0].name))
    #         if isinstance(self.on_hand[0], Weapon):
    #             self.unused_weapons.append(self.weapon)
    #             self.weapon = self.on_hand.popleft()
    #         else:
    #             self.unused_armors.append(self.armor)
    #             self.armor = self.on_hand.popleft()
    #     else:
    #         if isinstance(self.on_hand[0], Weapon):
    #             self.unused_weapons.append(self.on_hand.popleft())
    #         else:
    #             self.unused_armors.append(self.on_hand.popleft())
    #     self.pending = Pending.NONE
    #     print("miohitokiri")
    #     if self.on_hand:
    #         self.meet(self.on_hand[0], say)
    def change2(self, item_name):
        for item in self.unused_armors:
            if item.name == item_name:
                self.unused_armors.append(self.armor)
                self.armor = item
                self.unused_armors.remove(item)
                return item.name
        for item in self.unused_weapons:
            if item.name == item_name:
                self.unused_weapons.append(self.weapon)
                self.weapon = item
                self.unused_weapons.remove(item)
                return item.name
        return False
    def upgrade(self, item, out, times=1):
        blacksmith = self.on_hand.popleft()
        self.on_hand.append(blacksmith)
        assert(isinstance(blacksmith,Blacksmith))
        if item not in ["weapon","armor", "w", "a"]:
            out.send_wrong_argument()
            return
        try:
            times = int(times)
        except:
            times = 1
        updrade_times = 0
        while updrade_times < times:
            if not blacksmith.upgrades(item, self):
                out.send_upgrade_limited(updrade_times)
                break
            updrade_times += 1
        else:
            out.send_upgrade_full(updrade_times)
        self.pending = Pending.NONE
        if self.pending == Pending.NONE:
            self.meet(self.on_hand[0], out)
        
    def purchase(self, itemno, out):
        pprint(self.on_hand)
        print("before purchase")
        shop = self.on_hand.popleft()
        self.on_hand.append(shop)
        if shop.buy(self,itemno, out):
            pprint(self.on_hand)
            print("end of purchase")
        else:
            out.send_not_enough_coin()
        self.pending = Pending.NONE
        if self.pending == Pending.NONE:
            self.meet(self.on_hand[0], out)
        
    def recieve(self, money):
        self.coin += money
        # hmm
    def use_potion(self, potion, phase):
        self.hp = min(self.maxhp, self.hp + 0) # fill heel hp
        self.potions.remove(potion)
    def restart(self):
        self.pos = self.phase()*10
        self.hp = self.maxhp
        for i in self.on_hand:
            print("On hand event:", i)
        pass
    def add_exp(self, exp, out, said_msg):
        self.exp += exp
        while self.lvl < len(Exps) and self.exp >= Exps[self.lvl]:
            said_msg = out.send_level_up(self.name, self.lvl+1, said_msg)
            self.exp -= Exps[self.lvl]
            self.atk += LevelUp[self.lvl][0]
            self.dfd += LevelUp[self.lvl][1]
            self.maxhp += LevelUp[self.lvl][2]
            self.lvl += 1
            self.hp = self.maxhp
        return said_msg
    def level_to(self, level, out, said_msg):
        if self.lvl >= level:
            return
        while self.lvl < len(Exps) and self.lvl < level:
            self.atk += LevelUp[self.lvl][0]
            self.dfd += LevelUp[self.lvl][1]
            self.maxhp += LevelUp[self.lvl][2]
            self.lvl += 1
        self.hp = self.maxhp
        self.exp = 0
        return out.send_level_up(self.name, self.lvl, said_msg)
