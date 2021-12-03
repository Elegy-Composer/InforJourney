from abc import abstractmethod
from Data import Chests, Monsters, Weapons, Armors
from Item import Weapon, Armor
from Entity import Monster
from Events import Chest, Event
from random import choice, randrange
from pprint import pprint

def rand(things, weights):
    w = sum(weights)
    seed = randrange(w)
    total = 0
    for i in range(len(weights)):
        total += weights[i]
        if seed < total:
            #print(seed)
            return things[i]

class Gen(Event):
    def __init__(self):
        pass

    @abstractmethod
    def gen(self, player_level, phase) -> Event:
        pass

    def invoke_event(self, player, out, first_time):
        event = self.gen(player.lvl, player.phase())
        return event.invoke_event(player, out, first_time)

class MonsterGen(Gen):
    def __init__(self):
        pass
    def gen(self, player_level, phase):
        print("氣炸！！")
        l = []
        for name in Monsters[phase]:
            atk, dfd, hp, exp, coin, mini, maxi = Monsters[phase][name]
            if mini <= player_level <= maxi:
                l.append(Monster(name, atk, dfd, hp, exp, coin))
        pprint(choice(l))
        print("好氣喔")
        return choice(l)
        
class ChestGen(Gen):
    def __init__(self):
        pass
    def gen(self, player_level, phase):
        coin = rand(Chests[phase]['coin'], Chests[phase]['coin_weight'])
        weapon = rand(Chests[phase]['weapon'], Chests[phase]['weapon_weight'])
        if(weapon is not None):
            if(weapon in Weapons):
                weapon = Weapon(weapon)
            else:
                weapon = Armor(weapon)
        return Chest(coin, weapon)