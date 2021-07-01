from logging import makeLogRecord
from Entity import Entity, Monster
from Data import Positions
from Gen import Gen
from Events import Chest, Shop, Blacksmith
from Data import Pending, Exps, LevelUp
from Item import Weapon, Armor, Item
from pprint import pprint
from collections import deque

def Entity_type(entity):
    if isinstance(entity, Monster) :
        return "首領" if entity.is_boss else "小怪"
    else:
        return "玩家"

def chinese(data):
    count = 0
    for s in data:
        if ord(s) > 127:
            count += 1
    return count

class Player(Entity):
    def __init__(self, uid, name):
        super(Player, self).__init__(name, 30, 10, 5) # hp, at, dfd
        self.id = uid
        self.exp = 0
        self.maxhp = 30
        self.lvl = 1
        self.coin = 100
        self.pos = 0
        self.weapon = Weapon("短刀")
        self.armor = Armor("皮衣")
        self.on_hand = deque() # to change 
        self.potions = []
        self.unused_weapons = [Weapon("純白長槍"), Weapon("基加斯西達的樹枝"), Weapon("短刀")]
        self.unused_armors = [Armor("披風"), Armor("聖甲蟲鍊墜")]
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
    
    def meet(self, event, orig_say, first_time=False, markup=None):
        print("meet")
        said = False
        
        def say(*args, **kwargs):
            nonlocal said
            print("X:", args)
            if said:
                said = orig_say(*args, **kwargs, edit=said)
            else:
                said = orig_say(*args, **kwargs)
        
        if isinstance(event, Gen):
            return self.meet(event.gen(self.lvl,self.phase()),say)
        if isinstance(event,Entity):
            say("{}遇到了{} {}".format(self.name, Entity_type(event), event.name))
            res = self.fight(event, say)
            print(self.hp, event.hp)
            if event.hp <= 0: # Win
                if isinstance(event, Monster):
                    say("{}打倒了{} ，獲得了{}金幣和{}經驗值".format(self.name, event.name, event.coin, event.exp))
                    if(event.is_boss):
                        self.level_to(min(25*(self.phase()+1) + 1, 100), say)
                        if(self.phase() == 3):
                            say("恭喜{}通關遊戲".format(self.name))
                            return "Starburst"
                    self.add_exp(event.exp, say)
                    self.coin += event.coin
                else:
                    say("{}打倒了{}".format(self.name, event.name))
                    event.restart()
            elif self.hp <= 0:
                say("{}被{}打倒了 SAD".format(self.name, event.name))
                self.restart() 
            else :
                say("竟然是百年難得一見的平手")
            return True
        if isinstance(event, Shop):
            if first_time:
                say("{}抵達一間商店".format(self.name))
            msg = "```\n======歡迎來到商店======\n"
            for i, (item, price) in enumerate(zip(event.goods,event.price)):
                msgstr = '{0:{wd}}'.format(item.name,wd=15-chinese(item.name))
                msg+= "{}. {}{:>5}\n".format(i,msgstr,price)
            msg+="```"
            say(msg, "Markdown", markup=markup)
            self.pending = Pending.SHOP
            self.on_hand.append(event)
            return False
        if isinstance(event, Blacksmith):
            if first_time:
                say("{}抵達一間鐵匠鋪".format(self.name))
            say("======歡迎來到鐵匠鋪======\n"
               +"武器升級 攻防+{} 價格:{}金幣\n\n".format(event.upgrade, event.get_cost(self.weapon))
               +"防具升級 攻防+{} 價格:{}金幣\n".format(event.upgrade, event.get_cost(self.armor)), 
               markup=markup)
            self.pending = Pending.BLACKSMITH
            self.on_hand.append(event)
            return False
        elif(isinstance(event, Chest)):
            self.recieve(event.coin)
            print("fok yu")
            if event.weapon is None :
                say("{}在一個寶箱裡找到了 {} 金幣".format(self.name, event.coin))
            else:
                say("{}在一個寶箱裡找到了 {} 金幣和一個{}".format(self.name, event.coin, event.weapon.name))
                #self.ask_change(event.weapon,say)
                if isinstance(event.weapon):
                    self.unused_weapons.append(event.weapon)
                else:
                    self.unused_armors.append(event.weapon)
            return True
        else:
            pprint(event)
            return True

    def ask_change(self,item,say):
        self.on_hand.appendleft(item)
        if isinstance(item, Weapon):
            say("{}，你已獲得新武器：\n{}\n 攻+{} 防+{}\n是否將其替換舊有武器\n{}\n 攻+{} 防+{}".format(self.name, item.name, item.atk, item.dfd, self.weapon.name, self.weapon.atk, self.weapon.dfd))
        else:
            say("{}，你已獲得新防具：\n{}\n 攻+{} 防+{}\n是否將其替換舊有防具\n{}\n 攻+{} 防+{}".format(self.name, item.name, item.atk, item.dfd, self.armor.name, self.armor.atk, self.armor.dfd))
        self.pending = Pending.CHANGE

    def change(self, change, say):
        pprint(self.on_hand)
        assert(isinstance(self.on_hand[0],Item))
        if change:
            say("{}已成功裝備{}".format(self.name,self.on_hand[0].name))
            if isinstance(self.on_hand[0], Weapon):
                self.unused_weapons.append(self.weapon)
                self.weapon = self.on_hand.popleft()
            else:
                self.unused_armors.append(self.armor)
                self.armor = self.on_hand.popleft()
        else:
            if isinstance(self.on_hand[0], Weapon):
                self.unused_weapons.append(self.on_hand.popleft())
            else:
                self.unused_armors.append(self.on_hand.popleft())
        self.pending = Pending.NONE
        print("miohitokiri")
        if self.on_hand:
            self.meet(self.on_hand[0], say)
    def change2(self, item_name, say):
        for item in self.unused_armors:
            if item.name == item_name:
                self.unused_armors.append(self.armor)
                self.armor = item
                self.unused_armors.remove(item)
                say("{}已成功裝備{}".format(self.name, item.name))
                return
        for item in self.unused_weapons:
            if item.name == item_name:
                self.unused_weapons.append(self.weapon)
                self.weapon = item
                self.unused_weapons.remove(item)
                say("{}已成功裝備{}".format(self.name, item.name))
                return
        say("{}並未持有{}".format(self.name, item_name))
    def upgrade(self, item, say, times=1):
        blacksmith = self.on_hand.popleft()
        assert(isinstance(blacksmith,Blacksmith))
        self.pending = Pending.NONE
        if item not in ["weapon","armor", "w", "a"]:
            say("參數錯誤")
            return
        try:
            times = int(times)
        except:
            times = 1
        updrade_times = 0
        while updrade_times < times:
            if not blacksmith.upgrades(item, self):
                say("金幣不足 共升級{}次".format(updrade_times))
                break
            updrade_times += 1
        else:
            say("升級{}次成功".format(updrade_times))
        self.on_hand.append(blacksmith)

        if self.pending == Pending.NONE:
            self.meet(self.on_hand[0], say)
        
    def purchase(self, itemno, say):
        pprint(self.on_hand)
        print("before purchase")
        shop = self.on_hand.popleft()
        self.pending = Pending.NONE
        if shop.buy(self,itemno, say):
            # say("購買成功") written in shop.buy
            self.on_hand.append(shop)
            pprint(self.on_hand)
            print("end of purchase")
        else:
            say("金幣不足 購買失敗")
        if self.pending == Pending.NONE:
            self.meet(self.on_hand[0], say)
        
    def recieve(self, money):
        self.coin+= money
        # hmm
    def use_potion(self, potion, phase):
        self.hp = min(self.maxhp, self.hp + 0) # fill heel hp
        self.potions.remove(potion)
    def restart(self):
        self.pos = self.phase()*10
        self.hp = self.maxhp
        pass
    def add_exp(self, exp, say):
        self.exp += exp
        while self.exp >= Exps[self.lvl]:
            say("{}升到了{}級喔喔喔喔喔".format(self.name,self.lvl+1))
            self.exp -= Exps[self.lvl]
            self.lvl += 1
            self.atk += LevelUp[self.phase()][0]
            self.dfd += LevelUp[self.phase()][1]
            self.maxhp += LevelUp[self.phase()][2]
            self.hp = self.maxhp
    def level_to(self, level, say):
        if self.lvl >= level:
            return
        self.atk += LevelUp[self.phase()][0] * (level - self.lvl)
        self.dfd += LevelUp[self.phase()][1] * (level - self.lvl)
        self.maxhp += LevelUp[self.phase()][2] * (level - self.lvl)
        self.hp = self.maxhp
        self.exp = 0
        self.lvl = level
        say("{}升到了{}級喔喔喔喔喔".format(self.name,self.lvl))
