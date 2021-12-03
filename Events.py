from abc import ABC, abstractmethod

from num2words.lang_AR import ARABIC_ONES
from Data import Pending, BlacksmithParams, Shops, Potions
from Item import Item, Weapon, Armor, Potion

class Event(ABC):
    @abstractmethod
    def invoke_event(self, player, out, first_time):
        pass

class Chest(Event):
    def __init__(self, coin, weapon):
        self.coin = coin
        self.weapon = weapon
    
    def invoke_event(self, player, out, first_time):
        said_msg = None
        player.recieve(self.coin)
        print("fok yu")
        if self.weapon is None :
            said_msg = out.send_find_chest(player.name, self.coin, message=said_msg)
        else:
            said_msg = out.send_find_chest(player.name, self.coin, self.weapon.name, said_msg)
            if isinstance(self.weapon, Weapon):
                player.unused_weapons.append(self.weapon)
            else:
                player.unused_armors.append(self.weapon)
        return True

class Shop(Event):
    def __init__(self, phase):
        self.goods = []
        self.price = []
        for item in Shops[phase]:
            self.price.append(item[2])
            if(item[1] == 1):
                self.goods.append(Weapon(item[0]))
            if(item[1] == 2):
                self.goods.append(Armor(item[0]))
            if(item[1] == 3):
                self.goods.append(Potion(item[0], Potions[item[0]]))

    def buy(self, player, no, out):
        if player.coin < self.price[no]:
            return False
        
        player.coin -= self.price[no]
        item = self.goods[no]
        del self.goods[no]
        del self.price[no]
        out.send_buy_success()
        if isinstance(item, Weapon):
            #player.ask_change(item,say)
            player.unused_weapons.append(item)
        elif isinstance(item, Armor):
            player.unused_armors.append(item)
        else:
            player.potions.append(item)
        return True
    
    def invoke_event(self, player, out, first_time):
        said_msg = None
        if first_time:
            said_msg = out.send_reach_shop(player.name, said_msg)
        said_msg = out.send_shop_items(self.goods, self.price, said_msg)
        player.pending = Pending.SHOP
        if self not in player.on_hand:
            player.on_hand.append(self)
        return False

class Blacksmith(Event):
    def __init__(self, phase):
        self.upgrade, self.multi, self.add = BlacksmithParams[phase]
    def get_cost(self, item):
        return (item.level + self.add) * self.multi
    def upgrades(self, item,player):
        return self.upgrade_weapon(player) if item[0] == "w" else self.upgrade_armor(player)
    def upgrade_weapon(self, player):
        cost = self.get_cost(player.weapon)
        if player.coin >= cost:
            player.weapon.atk += self.upgrade
            player.weapon.dfd += self.upgrade
            player.coin -= cost
            return True
        else:
            return False
        
    def upgrade_armor(self, player):
        cost = self.get_cost(player.armor)
        if player.coin >= cost:
            player.armor.atk += self.upgrade
            player.armor.dfd += self.upgrade
            player.coin -= cost
            return True
        else:
            return False

    def invoke_event(self, player, out, first_time):
        said_msg = None
        if first_time:
            said_msg = out.send_reach_blacksmith(player.name, said_msg)
        said_msg = out.send_blacksmith_service(self.upgrade, self.get_cost(player.weapon), self.get_cost(player.armor), said_msg)
        player.pending = Pending.BLACKSMITH
        if self not in player.on_hand:
            player.on_hand.append(self)
        return False