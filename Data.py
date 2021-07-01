from enum import Enum
class Pending(Enum):
    NONE = 0
    BLACKSMITH = 1
    SHOP = 2
    CHANGE = 3
    RETIRE = 4
Exps = [ int(100*2**(i/10)) for i in range(100) ]
Weapons = {
    "短刀": (5, 0), 
    "長劍": (7, 3), 
    "弓": (10, 0), 
    "法杖": (5, 5), 
    "大劍": (20, 0), 
    "基加斯西達的樹枝": (25, 10), 
    
    "長矛":(20, 15), 
    "重錘":(40, 10),
    "三叉戟":(30, 20),
    "彎刀":(35, 15),
    "破咒之鍊":(50, 30),
    "法老權杖":(60, 40), 
    
    "光之杖": (35, 25),
    "雙手大斧": (60, 20),
    "十字鎬": (40, 40),
    "火把": (55, 25),
    "奪魂雙刀": (90, 10),
    "劇毒手杖": (100, 25), 
    
    "騎士之劍": (50, 30),
    "純白長槍": (60, 40),
    "斷罪之刃": (65, 35),
    "聖炎長弓": (75, 25),
    "誓約勝利之劍": (100, 50)
}

Armors = {
    "皮衣": (0, 3), 
    "鐵甲": (0, 5), 
    "披風": (3, 2), 
    "長袍": (5, 0),  
    "重甲": (0, 20), 
    "基加斯西達的樹皮": (10, 25), 
    
    "防風大衣":(5, 30),
    "戰鎧":(10, 40),
    "沙漠斗篷":(20, 30),
    "盜賊戰甲":(25, 25),
    "加護聖衣":(10, 70),
    "聖甲蟲鍊墜":(25, 75), 
    
    "牧師袍": (15, 40),
    "棘刺戰甲": (20, 55),
    "礦工裝備": (15, 60),
    "火焰鎧甲": (35, 40),
    "暗殺者風衣": (40, 60),
    "鼠骨戒指": (50, 75), 

    "白銀鎧甲": (25, 55),
    "破惡聖鎧": (40, 60),
    "審判者聖衣": (45, 55),
    "聖者戰袍": (30, 70),
    "雪花之壁": (0, 150)
}

Potions = {
    "恢復藥水(C)": (20, 60, 100, 200), 
    "恢復藥水(B)": (45, 90, 150, 250), 
    "恢復藥水(A)": (70, 120, 200, 300),
}

#Starter = (Weapon("短刀"), Armor("皮衣"))
#PlayerData = (10, 5, 30) # atk, dfd, hp

Chests =  [
        {
            "coin": (5, 10, 25, 50),
            "coin_weight": (10, 5, 3, 2),
            "weapon": (
                None, "長劍", "弓", "法杖", "鐵甲", "披風", "長袍", "大劍", "重甲"
            ),
            "weapon_weight": (80, 3, 3, 3, 3, 3, 3, 1)
        }, 
        {
            "coin": (25, 50, 100, 150),
            "coin_weight": (10, 5, 3, 2),
            "weapon": (
                None, "重錘", "三叉戟", "彎刀", "戰鎧", "沙漠斗篷", "盜賊護甲", "破咒之鍊", "加護聖衣"
            ),
            "weapon_weight": (80, 3, 3, 3, 3, 3, 3, 1)
        }, 
        {
            "coin": (100, 150, 250, 400),
            "coin_weight": (10, 5, 3, 2),
            "weapon": (
                None, "雙手大斧", "十字鎬", "火把", "棘刺戰甲", "礦工裝備", "火焰鎧甲", "奪魂雙刀", "暗殺者風衣"
            ),
            "weapon_weight": (80, 3, 3, 3, 3, 3, 3, 1)
        }, 
        {
            "coin": (500, 750, 1000, 1500),
            "coin_weight": (10, 5, 3, 2),
            "weapon": (
                None, "純白長槍", "斷罪之刃", "聖炎長弓", "破惡聖鎧", "審判者聖衣", "聖者戰袍", "誓約勝利之劍", "雪花之壁"
            ),
            "weapon_weight": (80, 3, 3, 3, 3, 3, 3, 1)
        }, 
    ]

Shops = [
        [
            ("長劍", 1,  50),
            ("弓", 1, 50),
            ("法杖", 1, 50),
            ("鐵甲", 2, 70),
            ("披風", 2, 70),
            ("長袍", 2, 70),
            ("恢復藥水(C)", 3, 30), 
            ("恢復藥水(B)", 3, 50), 
            ("恢復藥水(A)", 3, 100),
        ], 
        [
            ("重錘", 1, 250),
            ("三叉戟", 1, 250),
            ("彎刀", 1, 250),
            ("戰鎧", 2, 300),
            ("沙漠斗篷", 2, 300),
            ("盜賊戰甲", 2, 300),
            ("恢復藥水(C)", 3, 80),
            ("恢復藥水(B)", 3, 120),
            ("恢復藥水(A)", 3, 180),
        ], 
        [
            ("雙手大斧", 1, 500),
            ("十字鎬", 1, 500),
            ("火把", 1, 500),
            ("棘刺戰甲", 2, 650),
            ("礦工裝備", 2, 650),
            ("火焰鎧甲", 2, 650),
            ("恢復藥水(C)", 3, 200),
            ("恢復藥水(B)", 3, 300),
            ("恢復藥水(A)", 3, 400)
        ], 
        [
            ("純白長槍", 1, 1500),
            ("斷罪之刃", 1, 1500),
            ("聖炎長弓", 1, 1500),
            ("破惡聖鎧", 2, 2000),
            ("審判者聖衣", 2, 2000),
            ("聖者戰袍", 2, 2000),
            ("恢復藥水(C)", 3, 400),
            ("恢復藥水(B)", 3, 500),
            ("恢復藥水(A)", 3, 600)
        ]
    ]
    # atk, dfd, hp, exp, coin, is_boss, min, max
Monsters = [
        {
            "史萊姆": (10, 0, 10, 10, 3, 0, 1, 5), 
            "地精": (15, 3, 15, 15, 7, 0, 1, 10), 
            "毒蜂": (20, 5, 20, 25, 10, 0, 1, 15), 
            "樹怪": (25, 10, 30, 40, 15, 0, 6, 20), 
            "獸人戰士": (30, 15, 50, 70, 20, 0, 11, 25), 
            "石巨人": (40 ,25 ,70 , 70, 30, 0, 16, 25), 
            "森之魂": (50, 30, 80, 80, 35, 0, 21, 100), 
        }, 
        {
            "沙怪": (75, 40, 100, 100, 40, 0, 26, 30),
            "巨型蟻獅": (85, 45, 110, 105, 50, 0, 26, 35), 
            "沙漠亡魂": (95, 50, 115, 110, 55, 0, 26, 40),
            "魔蠍": (100, 55, 125, 120, 60, 0, 31, 45),
            "木乃伊": (110, 60, 135, 125, 70, 0, 36, 50),
            "詛咒棺木": (125, 70, 150, 145, 85, 0, 41, 50),
            "阿努比斯": (150, 80, 160, 150, 90, 0, 46, 100)
        },
        {
            "洞穴蜘蛛": (160, 90, 175, 160, 100, 0, 51, 55),
            "骷髏": (170, 95, 180, 165, 110, 0, 51, 60),
            "吸血蝙蝠": (185, 100, 190, 170, 115, 0, 51, 65),
            "怨靈": (195, 105, 195, 185, 120, 0, 56, 70),
            "水晶魔像": (205, 120, 200, 200, 130, 0, 61, 75),
            "影魔": (215, 120, 200, 210, 140, 0, 66, 75),
            "死徒": (225, 125, 220, 225, 150, 0, 71, 75)
        },
        {
            "暗黑僕從": (275, 180, 300, 750, 300, 0, 76, 80),
            "暴虐惡魔": (300, 200, 325, 775, 325, 0, 76, 85),
            "窺探者": (320, 225, 350, 800, 350, 0, 76, 90),
            "詛咒騎士": (350, 250, 375, 850, 400, 0, 81, 95),
            "漆黑魔獸": (400, 300, 425, 900, 450, 0, 86, 100),
            "萬惡巨人": (450, 350, 450, 1000, 500, 0, 91, 100),
            "護王魔神": (500, 400, 500, 1200, 750, 0, 96, 100)

        }
    ]
Bosses = [
        ("惡魔之樹．基加斯西達", 70, 70, 150, 200, 100, 1, 1, 100),
        ("人面獅身獸．斯芬克斯", 175, 100, 200, 400, 150, 1, 1, 100),
        ("溝鼠之王．瑞特昆恩", 250, 160, 275, 350, 500, 1, 1, 100),
        ("原初之惡．桑德拉傑爾邱斯", 600, 500, 600, 0, 0, 1, 1, 100),
    ]
    
BlacksmithParams =  [(1, 5, 1), (2, 8, 5), (3, 15, 10), (4, 20, 15)]
# upgrade, multi, add

LevelUp = [(2, 2, 4), (4, 4, 6), (8, 8, 10), (16, 16, 20)]

Positions = {
    "Boss": [10, 20, 30, 40],
    "Blacksmith": [9, 17, 26, 37],
    "Shop": [5, 16, 28, 35], 
    "ChestGen": [2, 8, 11, 13, 23, 29, 32, 39]
}