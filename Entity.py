class Entity:
    def __init__(self, name, hp, atk, dfd):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.dfd = dfd
        
    def fight(self, B, say):
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
        while 1:
            # Attack Phase
            B.hp -= a_dmg
            say("{} 攻擊 {}，{} 剩下 {} 滴血".format(A.name, B.name, B.name, max(B.hp, 0)))
            

            # HP Judge Phase
            if B.hp <= 0:
                return A # Return the Winner!!!!!

            A, B = B, A # Malignant
            a_dmg, b_dmg = b_dmg, a_dmg




class Monster(Entity):
    def __init__(self, name, atk, dfd, hp, exp, coin, is_boss):
        super(Monster, self).__init__(name, hp, atk, dfd)
        self.exp = exp
        self.coin = coin
        self.is_boss = is_boss
