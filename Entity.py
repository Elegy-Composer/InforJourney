from random import uniform
from Item import Armor, Weapon


class Entity:
    def __init__(self, name, hp, atk, dfd):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.dfd = dfd
        
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




class Monster(Entity):
    def __init__(self, name, atk, dfd, hp, exp, coin):
        super(Monster, self).__init__(name, hp, atk, dfd)
        self.exp = exp
        self.coin = coin

class Boss(Monster):
    def __init__(self, name, atk, dfd, hp, exp, coin, drop_item):
        super(Boss, self).__init__(name, atk, dfd, hp, exp, coin)
        if drop_item[0]:
            self.drop_item = (Weapon(drop_item[0]), Armor(drop_item[1]))
        else:
            self.drop_item = (None, None)
    def drop(self):
        dropped = self.drop_item
        self.drop_item = (None, None)
        return dropped