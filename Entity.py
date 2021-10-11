from random import uniform
from Events import Event
from Item import Armor, Weapon


class Entity(Event):
    def __init__(self, name, hp, atk, dfd):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.dfd = dfd

    def entity_type(self):
        return "Entity"
        
    def fight(self, B):
        A = self
        a_dmg = A.atk - B.dfd
        b_dmg = B.atk - A.dfd
        print(a_dmg, b_dmg)
        print(A.name,A.atk,A.dfd)
        print(B.name,B.atk,B.dfd)
        if(hasattr(A,"weapon")):
            a_dmg+=A.weapon.atk+A.armor.atk
            b_dmg-=A.weapon.dfd+A.armor.dfd
        if(hasattr(B,"weapon")):
            b_dmg+=B.weapon.atk+B.armor.atk
            a_dmg-=B.weapon.dfd+B.armor.dfd
        print(a_dmg, b_dmg)
        a_dmg = max(a_dmg,0)
        b_dmg = max(b_dmg,0)
        if a_dmg == 0 and b_dmg == 0:
            print("垃圾互打")
            return;
        fight_str = ""
        while 1:
            # Attack Phase
            dmg = round(a_dmg * uniform(0.9, 1.1))
            B.hp -= dmg
            fight_str += "{} 攻擊 {}，{} 剩下 {} 滴血\n".format(A.name, B.name, B.name, max(B.hp, 0))
            

            # HP Judge Phase
            if B.hp <= 0:
                return fight_str

            A, B = B, A # Malignant
            a_dmg, b_dmg = b_dmg, a_dmg

    def invoke_event(self, player, out, first_time):
        said_msg = None
        said_msg = out.send_meet(player.name, self.entity_type(), self.name, said_msg)
        print("after send_meet, said_msg:")
        if said_msg:
            print(said_msg)
        else:
            print("None")
        res = player.fight(self)
        said_msg = out.send_fight_result(res, said_msg)
        print(player.hp, self.hp)
        if self.hp <= 0: # Win
            if isinstance(self, Monster):
                said_msg = out.send_beat(player.name, self.name, self.coin, self.exp, said_msg)
                if(isinstance(self, Boss)):
                    said_msg = player.level_to(min(10*(player.phase()+1) + 1, 40), out, said_msg)
                    if(player.phase() == 3):
                        said_msg = out.send_congrats_clear(player.name, said_msg)
                        return "Starburst"
                    drop_weapon, drop_armor = self.drop()
                    if drop_weapon:
                        player.unused_weapons.append(drop_weapon)
                        player.unused_armors.append(drop_armor)
                        said_msg = out.send_last_strike(player.name, drop_weapon.name, drop_armor.name, said_msg)
                said_msg = player.add_exp(self.exp, out, said_msg)
                player.coin += self.coin
            else:
                said_msg = out.send_beat(player.name, self.name, said_msg)
                self.restart()
        elif player.hp <= 0:
            said_msg = out.send_beaten(player.name, self.name, said_msg)
            player.restart()
        else :
            said_msg = out.send_tie(said_msg)
            if isinstance(self, Boss):
                player.restart()
        return True


class Monster(Entity):
    def __init__(self, name, atk, dfd, hp, exp, coin):
        super(Monster, self).__init__(name, hp, atk, dfd)
        self.exp = exp
        self.coin = coin
    
    def entity_type(self):
        return "小怪"

class Boss(Monster):
    def __init__(self, name, atk, dfd, hp, exp, coin, drop_item):
        super(Boss, self).__init__(name, atk, dfd, hp, exp, coin)
        if drop_item[0]:
            self.drop_item = (Weapon(drop_item[0]), Armor(drop_item[1]))
        else:
            self.drop_item = (None, None)
    
    def entity_type(self):
        return "首領"

    def drop(self):
        dropped = self.drop_item
        self.drop_item = (None, None)
        return dropped