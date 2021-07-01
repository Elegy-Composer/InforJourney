from random import randrange

from num2words.lang_AR import ARABIC_ONES
from Data import Pending, BlacksmithParams, Shops, Potions
from Item import Item, Weapon, Armor, Potion


class Chest:
    def __init__(self, coin, weapon):
        self.coin = coin
        self.weapon = weapon
class EventCanEnd:
    pass
class Shop(EventCanEnd):
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

    def buy(self, player, no, say):
        if player.coin < self.price[no]:
            return False
        
        player.coin -= self.price[no]
        item = self.goods[no]
        del self.goods[no]
        del self.price[no]
        say("購買成功")
        if isinstance(item, Weapon):
            #player.ask_change(item,say)
            player.unused_weapons.append(item)
        elif isinstance(item, Armor):
            player.unused_armors.append(item)
        else:
            player.potions.append(item)
        return True

class Blacksmith(EventCanEnd):
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
