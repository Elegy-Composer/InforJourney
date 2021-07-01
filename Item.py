from Data import Weapons, Armors, Potions

class Item:
    def __init__(self, name, atk, dfd):
        self.name = name
        self.atk = atk
        self.dfd = dfd
        self.level = 0
        
class Weapon(Item):
    def __init__(self, name):
        super(Weapon, self).__init__(*((name, ) + Weapons[name]))

class Armor(Item):
    def __init__(self, name):
        super(Armor, self).__init__(*((name, ) + Armors[name]))

class Potion:
    def __init__(self, name, heal):
        self.name = name
        self.heal = heal
    def __str__(self):
        return self.name
    def drink(self, player):
        player.hp = min(player.maxhp, player.hp + self.heal[player.phase()])
        return self.heal[player.phase()]
