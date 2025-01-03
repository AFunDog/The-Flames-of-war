from operator import truediv
import wave
import pyaudio
from playsound import playsound
import pygame
import random
import time
from pygame.examples.audiocapture import sound

######################1窗口和初始化################

# 初始化所有pygame的函数
pygame.init()

# 创建一个屏幕
screen = pygame.display.set_mode((450, 720))#主屏幕

# 输出游戏窗口的标题
pygame.display.set_caption("战争烈焰")

# 定义一个时钟
clock = pygame.time.Clock()

#定义一种字体，用于后续提示
font = pygame.font.Font(None, 24)

'''逻辑:不用数组，而是使用左上角和右下角来描述一个物块，每一个障碍物设置一个判定函数，这样可以落实到每一个像素的判定，而又不会占用过多空间
部分位置对应的左上角像素坐标
[0][0] [0][1] [0][2]   (115, 0)   (195, 0)   (275, 0)    (355,0)
[1][0] [1][1] [1][2]   (115, 80)  (195, 80)  (275, 80)
[2][0] [2][1] [2][2]   (115, 160) (195, 160) (275, 160)
[3][0] [3][1] [3][2]   (115, 240) (195, 240) (275, 240)
[4][0] [4][1] [4][2]   (115, 320) (195, 320) (275, 320)
[5][0] [5][1] [5][2]   (115, 400) (195, 400) (275, 400)
[6][0] [6][1] [6][2]   (115, 480) (195, 480) (275, 480)
[7][0] [7][1] [7][2]   (115, 560) (195, 560) (275, 560)
[8][0] [8][1] [8][2]   (115, 640) (195, 640) (275, 640)
'''

###############################2基本处理函数################
'''
企划:
1.你想做个什么样的游戏-大纲:我想在赛车的基础上，缝合一些飞机大战的要素，收集了道具后，还可以有一些割草之类的效果
2.部分可以做的细节{

（1）.碰撞后箱子裂开的特效
(2).发射武器的道具
（3）.一个BOSS
（4）转弯效果
（5）冲击波特效

}
3.流程：先把几种障碍物实现出来，然后以合适的方法安排它们上场就好了
4.流程2.0：收尾前，还要完成：boss和子弹的碰撞
5.还要做到的:    开局动画（开始游戏那个），死亡界面，胜利界面
'''

#转换函数,输入图片的左上角的坐标，转换为逻辑数组中的位置
def transform_toLogical(x,y):
    x-=115
    list=[int(x/80),int(y/80)]
    return list


#转换函数，输入逻辑数组中的位置，转换为图片应该有的左上角
def transform_toImage(x,y):
    #图片的初始值
    list=[115,0]
    for _ in range(x):
        list[0]+=80
    for _ in range(y):
        list[1]+=80
    return list


#####################3基本背景#############

#游戏背景图片,拉伸图片，使其可以覆盖全屏
image_background = pygame.transform.scale(pygame.image.load("image/background.jpg"), (450, 720))
image_start_background=pygame.transform.scale(pygame.image.load("image/start_background.png"), (450, 720))
#游戏跑道图片
image_runway=pygame.image.load("image/runway.png")
start_image=40;end_image=760 #截取图片的部分，做出动态效果


######################4.定义玩家和障碍物,道具等等，逻辑################


#玩家类
class Player:

    #构造函数
    def __init__(self):
        # (旧)载入玩家的图像(两个状态)
        self.image = pygame.transform.scale(pygame.image.load("image/player.png"), (40, 100))
        self.image2 = pygame.transform.scale(pygame.image.load("image/player2.png"), (40, 100))
        self.now=0#判断玩家的两种绘图状态

        # 设置玩家的初始位置，xy是玩家左上角的坐标，x2y2是右下角
        self.x = 195;   self.y = 320
        self.x2 = self.x + 40;  self.y2 = self.y + 100

        # 这两个用于后续定义按下按键期间，每帧玩家可以移动的距离
        self.y_change = 0;  self.x_change = 0

        #生命值，蓄力值作为状态参数，定义在运行部分
        pass

        #护盾光环特效
        self.image_light=[0 for _ in range(8)]
        self.image_light[1] = pygame.transform.scale(pygame.image.load("image/light/light1.png"), (160, 160))
        self.image_light[2] = pygame.transform.scale(pygame.image.load("image/light/light2.png"), (160, 160))
        self.image_light[3] = pygame.transform.scale(pygame.image.load("image/light/light3.png"), (160, 160))
        self.image_light[4] = pygame.transform.scale(pygame.image.load("image/light/light4.png"), (160, 160))
        self.image_light[5] = pygame.transform.scale(pygame.image.load("image/light/light5.png"), (160, 160))
        self.image_light[6] = pygame.transform.scale(pygame.image.load("image/light/light6.png"), (160, 160))
        self.if_light=0#判断是否要加上光效
        self.now_light=1#判断当前光效状态,用于刷新图像

        #机枪特效
        self.image_weapon_mian=pygame.transform.scale(pygame.image.load("image/weapon_main.png"), (25, 70))
        self.if_light = 0  # 判断是否要加上机枪

    # 更新玩家的坐标的数据,不能越界
    def update(self):
        if 112 < self.x+self.x_change < 320:
            self.x+=self.x_change
        if 0 < self.y +self.y_change < 640:
            self.y += self.y_change
        #同步更新右下角
        self.x2 = self.x + 40;self.y2 =self.y + 100

        # 防止超出或者低于屏幕
        if self.y < 0:
            self.y = 0
        elif self.y > 600 - self.image.get_height():
            self.y = 600 - self.image.get_height()

    #以数组形式，对外界输出当前的坐标
    def output_place(self):
        self.list=[[self.x,self.y],[self.x2,self.y2]]
        return self.list

    # 把玩家的位置绘制到屏幕上,有基本的动态效果
    def draw(self, screen, ifOpen):
        #绘制玩家本体
        if self.now==1:
            screen.blit(self.image, (self.x, self.y))
            self.now=2
        else:
            screen.blit(self.image2, (self.x, self.y))
            self.now=1

        # 绘制护盾光环
        if ifOpen==1:#如果护盾还生效，就开启
            if self.now_light<6:
                self.now_light+=1
            else:
                self.now_light=1

            screen.blit(self.image_light[self.now_light], (self.x-60, self.y-30))

        #绘制机枪
        screen.blit(self.image_weapon_mian, (self.x+7.5, self.y+15))

    #按下/放下，上下左右键的效果
    def left(self):
        self.x_change = -7.5

    def left_up(self):#释放按键
        self.x_change = 0

    def right(self):
        self.x_change = 7.5

    def right_up(self):
        self.x_change = 0

    def up(self):
        #前进的速度是最快的
        self.y_change=-10

    def up_up(self):
        #前进的速度是最快的
        self.y_change=0

    def down(self):
        self.y_change = 5

    def down_up(self):
        self.y_change = 0

#炮弹类
class shell:

    # 构造函数
    def __init__(self,list):
        # 载入障碍物的图像并且调节尺寸
        self.image = pygame.transform.scale(pygame.image.load("image/shell.png"), (25, 25))

        # 碰撞爆炸的图片
        self.image_bomb = pygame.transform.scale(pygame.image.load("image/bomb.png"), (50, 50))

        # 是否被碰撞（只伤害敌人一次）
        self.ifCollision = 0

        # 初始左上角坐标设置,要结合玩家的位置来
        self.y = list[0][1];    self.x = list[0][0]+7

        # 同步右下角坐标
        self.x2 = self.x + 25;  self.y2 = self.y + 25

        # 统一跟新数据的函数

    #更新状态的函数
    def update(self):
        # 障碍物的平移是y轴方向
        self.y -= 20

        # 同步右下角
        self.y2 = self.y + 25

    # 绘制函数
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # 判断炮弹是否撞上了boss，并且执行特定效果的函数,因为炮弹比飞机小，因此两者的比较逻辑不同
    def collision(self, list):
        if self.ifCollision == 0:
            if ((self.x < list[1][0] and self.x2 > list[0][0]) or #在炮弹在伤害判断区间的正中间
                (self.x < list[0][0] < self.x2) or (self.x < list[1][0] < self.x2)) and \
                    (self.y<list[1][1]):
                # 已经碰撞，则记录，绘制爆炸效果，并且向外界明确已经碰撞
                self.ifCollision = 1
                screen.blit(self.image_bomb, (self.x-12.5, self.y))
                return 1
            return 0
        else:
            return 0

    # 判断炮弹是否已经超出屏幕，准备删除的函数
    def is_off(self):
            if self.y < -20:
                return 1
            else:
                return 0


#BOSS类
class Boss:
    # 构造函数
    def __init__(self):
        # 载入BOSS的图像(六个状态)
        self.list_image=[0,0,0,0,0,0,0]
        self.list_image[1] = pygame.transform.scale(pygame.image.load("image/BOSS.png"), (280, 180))
        self.list_image[2] = pygame.transform.scale(pygame.image.load("image/BOSS.png"), (281, 180.5))
        self.list_image[3] = pygame.transform.scale(pygame.image.load("image/BOSS.png"), (282, 181))
        self.list_image[4] = pygame.transform.scale(pygame.image.load("image/BOSS.png"), (283, 181.5))
        self.list_image[5] = pygame.transform.scale(pygame.image.load("image/BOSS.png"), (284, 182))
        self.list_image[6] = pygame.transform.scale(pygame.image.load("image/BOSS.png"), (285, 182.5))
        self.now = 1  # 用来确定现在播放的是几号图片的变量，用来表现一定的动态效果
        self.down =0  # 判断让图片逐渐放大还是逐渐缩小

        # 设置BOSS的初始位置，xy是玩家左上角的坐标，x2y2是右下角
        self.x = 95; self.y = 0
        self.x2 = self.x + 40;self.y2 = self.y + 100

        # 生命值，蓄力值作为状态参数，定义在运行部分
        pass

    # 更新BOSS的坐标的数据,不能越界(因为BOSS不能移动，所以这一段暂时没有用)
    def update(self):
        if 112 < self.x + self.x_change < 320:
            self.x += self.x_change
        if 0 < self.y + self.y_change < 640:
            self.y += self.y_change
        # 同步更新右下角
        self.x2 = self.x + 40;self.y2 = self.y + 100

        # 防止超出或者低于屏幕
        if self.y < 0:
            self.y = 0
        elif self.y > 600 - self.image.get_height():
            self.y = 600 - self.image.get_height()

    # 以数组形式，对外界输出当前的坐标，对BOSS就是攻击有效区间
    def output_place(self):
        self.list = [[215, 0], [265, 180]]
        return self.list

    # 把BOSS的位置绘制到屏幕上,并且有基本的动态效果
    def draw(self, screen):
        # 绘制动态BOSS本体
        if self.down==0 and self.now < 6:
            self.now+=1
        elif self.down==0 and self.now==6:
            self.down=1
        elif self.down==1 and self.now>1:
            self.now-=1
        elif self.down==1 and self.now==1:
            self.down=0

        screen.blit(self.list_image[self.now], (self.x-self.now, self.y))

#障碍物-轮胎
class Obstacle_tire:

    #构造函数
    def __init__(self):
        # 载入障碍物的图像
        self.image = pygame.image.load("image/obstacle_tire.png")
        self.image = pygame.transform.scale(self.image, (50, 50))

        #是否被碰撞（只扣一次分数）
        self.ifCollision=0
        self.x_change = 0#碰撞后的移动方向

        # 初始左上角坐标设置
        self.y = -50;self.x = random.randint(115, 305)# 其中y超出屏幕，即不显示，随机生成x的值，即障碍物刷新后离你很近或者较远

        # 同步右下角坐标
        self.x2 = self.x + 50;self.y2 = self.y + 50

    #统一跟新数据的函数
    def update(self):
        # 障碍物的平移是y轴方向
        self.y += 10

        #同步右下角
        self.y2 = self.y + 50

        self.x+=self.x_change#碰撞效果

        # 将障碍物绘制到屏幕上

    #把图片绘制到屏幕上的函数
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    #判断障碍物是否撞上了玩家，并且执行特定效果的函数
    def collision(self, list):
        if self.ifCollision==0:
            if ((self.x < list[1][0] and self.x2 > list[0][0]) or
                (self.x < list[0][0] and self.x2 > list[1][0])) and \
                 ((self.y < list[1][1] and self.y2 > list[0][1]) or
                     (self.y < list[0][1] and self.y2 > list[1][1])):
                #已经碰撞，则记录
                self.ifCollision = 1
                #
                if (self.x+self.x2)/2>=((list[1][0]+list[0][0])/2) :
                    self.x_change=10
                else:
                    self.x_change=-10
                return 1
            return 0
        else:
            return 0

    #判断障碍物是否已经超出屏幕，准备删除的函数
    def is_off(self):
        if self.y >= 720:
            return 1
        else:
            return 0

#障碍物-炸弹
class Obstacle_bomb:
    # 构造函数
    def __init__(self):
        # 载入障碍物的图像
        self.image = pygame.transform.scale(pygame.image.load("image/obstacle_bomb.png"), (50, 50))
        # 碰撞爆炸的图片
        self.image_bomb = pygame.transform.scale(pygame.image.load("image/bomb.png"), (100, 100))

        # 是否被碰撞（只扣一次分数）
        self.ifCollision = 0

        # 初始左上角坐标设置
        self.y = 100;self.x = 210

        # 同步右下角坐标
        self.x2 = self.x + 50;self.y2 = self.y + 50

    # 统一跟新数据的函数
    def update(self):
        # 障碍物的平移是y轴方向
        self.y += 15

        # 同步右下角
        self.y2 = self.y + 50

    # 把图片绘制到屏幕上的函数
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # 判断障碍物是否撞上了玩家，并且执行特定效果的函数
    def collision(self, list):
        if self.ifCollision == 0:
            if ((self.x < list[1][0] and self.x2 > list[0][0]) or
                (self.x < list[0][0] and self.x2 > list[1][0])) and \
                    ((self.y < list[1][1] and self.y2 > list[0][1]) or
                     (self.y < list[0][1] and self.y2 > list[1][1])):
                # 已经碰撞，则记录
                self.ifCollision = 1
                #爆炸效果
                screen.blit(self.image_bomb, (self.x - 25, self.y))
                return 1
            return 0
        else:
            return 0

    # 判断障碍物是否已经超出屏幕，准备删除的函数
    def is_off(self):
        if self.y >= 720:
            return 1
        else:
            return 0

#道具类-治疗
class Prop_heal:
    # 构造函数
    def __init__(self):
        # 载入障碍物的图像
        self.image = pygame.image.load("image/heal.png")
        self.image = pygame.transform.scale(self.image, (35, 35))

        # 是否被碰撞（只扣一次分数）
        self.ifCollision = 0

        # 初始左上角坐标设置
        self.y = -50;
        self.x = random.randint(115, 305)  # 其中y超出屏幕，即不显示，随机生成x的值，即障碍物刷新后离你很近或者较远

        # 同步右下角坐标
        self.x2 = self.x + 35;self.y2 = self.y + 35

    # 统一跟新数据的函数
    def update(self):
        # 障碍物的平移是y轴方向
        self.y += 12.5

        # 同步右下角
        self.y2 = self.y + 35

    # 把图片绘制到屏幕上的函数
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # 判断障碍物是否撞上了玩家，并且执行特定效果的函数
    def collision(self, list):
        if self.ifCollision == 0:
            if ((self.x < list[1][0] and self.x2 > list[0][0]) or
                (self.x < list[0][0] and self.x2 > list[1][0])) and \
                    ((self.y < list[1][1] and self.y2 > list[0][1]) or
                     (self.y < list[0][1] and self.y2 > list[1][1])):
                # 已经碰撞，则记录
                self.ifCollision = 1
                return 1
            return 0
        else:
            return 0

    # 判断障碍物是否已经超出屏幕，准备删除的函数
    def is_off(self):
        if self.y >= 720:
            return 1
        else:
            return 0

#道具类-护盾
class Prop_shield:
    # 构造函数
    def __init__(self):
        # 载入障碍物的图像
        self.image = pygame.image.load("image/shield.png")
        self.image = pygame.transform.scale(self.image, (35, 35))

        # 是否被碰撞
        self.ifCollision = 0

        # 初始左上角坐标设置
        self.y = -50;
        self.x = random.randint(115, 305)  # 其中y超出屏幕，即不显示，随机生成x的值，即障碍物刷新后离你很近或者较远

        # 同步右下角坐标
        self.x2 = self.x + 35;
        self.y2 = self.y + 35

    # 统一跟新数据的函数
    def update(self):
        # 障碍物的平移是y轴方向
        self.y += 12.5

        # 同步右下角
        self.y2 = self.y + 35

    # 把图片绘制到屏幕上的函数
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # 判断障碍物是否撞上了玩家，并且执行特定效果的函数
    def collision(self, list):
        if self.ifCollision == 0:
            if ((self.x < list[1][0] and self.x2 > list[0][0]) or
                (self.x < list[0][0] and self.x2 > list[1][0])) and \
                    ((self.y < list[1][1] and self.y2 > list[0][1]) or
                     (self.y < list[0][1] and self.y2 > list[1][1])):
                # 已经碰撞，则记录
                self.ifCollision = 1
                return 1
            return 0
        else:
            return 0

    # 判断障碍物是否已经超出屏幕，准备删除的函数
    def is_off(self):
        if self.y >= 720:
            return 1
        else:
            return 0
#道具类-闪电
class Prop_lightning:
    # 构造函数
    def __init__(self):
        # 载入障碍物的图像
        self.image = pygame.image.load("image/lightning_icon.png")
        self.image = pygame.transform.scale(self.image, (35, 35))

        # 是否被碰撞（只扣一次分数）
        self.ifCollision = 0

        # 初始左上角坐标设置
        self.y = -50;
        self.x = random.randint(115, 305)  # 其中y超出屏幕，即不显示，随机生成x的值，即障碍物刷新后离你很近或者较远

        # 同步右下角坐标
        self.x2 = self.x + 35;
        self.y2 = self.y + 35

    # 统一跟新数据的函数
    def update(self):
        # 障碍物的平移是y轴方向
        self.y += 12.5

        # 同步右下角
        self.y2 = self.y + 35

    # 把图片绘制到屏幕上的函数
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # 判断障碍物是否撞上了玩家，并且执行特定效果的函数
    def collision(self, list):
        if self.ifCollision == 0:
            if ((self.x < list[1][0] and self.x2 > list[0][0]) or
                (self.x < list[0][0] and self.x2 > list[1][0])) and \
                    ((self.y < list[1][1] and self.y2 > list[0][1]) or
                     (self.y < list[0][1] and self.y2 > list[1][1])):
                # 已经碰撞，则记录
                self.ifCollision = 1
                return 1
            return 0
        else:
            return 0

    # 判断障碍物是否已经超出屏幕，准备删除的函数
    def is_off(self):
        if self.y >= 720:
            return 1
        else:
            return 0


###################################5运行#########################
############ 初始化玩家,Boss和障碍物列表
player = Player()
Boss = Boss()
obstacle_tire_all = []#用于收录所有轮胎
obstacle_bomb_all = []#用于收录所有的炸弹
shell_player = []#用于收录玩家子弹的对象
prop_heal_all = []#用于收录所有治疗道具
prop_shield_all = []#用于收录所有护盾道具
prop_lightning_all = []#用于收录所有闪电道具

#####声音################
pygame.mixer.init()
sound_all = pygame.mixer.Sound('bgm/all_bgm.wav')
sound_start = pygame.mixer.Sound('bgm/start_bgm.wav')
sound_lightning=pygame.mixer.Sound("bgm/lightning_bgm.wav")
sound_bomb = pygame.mixer.Sound("bgm/bomb_bgm.wav")
sound_win = pygame.mixer.Sound("bgm/win_bgm.wav")
sound_lose = pygame.mixer.Sound("bgm/lose_bgm.mp3")
##############一些状态参数

accumulator_obstacle=0#时间累加器，积累一定时间刷新一个障碍物-轮胎
accumulator_obstacle_bomb=0#累加器，固定生成障碍物-炸弹
accumulator_shell=0#固定生成玩家子弹
accumulator_heal=0#固定生成治疗
accumulator_shield=0#固定生成护盾
accumulator_lightning=0#固定生成闪电
image_hitPoint=pygame.transform.scale(pygame.image.load("image/HP.png"), (100, 20))
image_defencePoint=pygame.transform.scale(pygame.image.load("image/DP.png"), (100, 20))
image_hitPoint2=pygame.transform.scale(pygame.image.load("image/HP.png"), (450, 20))



############# 游戏运行过程 ##########

is_over = True
start = True
while is_over:
    victory=-1#胜利状态判定
    hitPoint=100#玩家生命值,以及其图片
    defencePoint=0#玩家护盾值，以及其图片
    ifOpen=0    #判断是否张开了护盾
    hitPoint2=450#BOSS生命值,以及其图片，因为屏幕的关系，最多450，想要减少的慢一点就降低子弹伤害
    lightning_time=0
    running = True
    sound_all_get = sound_all.play(-1)
    sound_all_get.pause()
    sound_win_get = sound_win.play(-1)
    sound_win_get.pause()
    sound_lose_get = sound_lose.play(-1)
    sound_lose_get.pause()
    while start:
        sound_all_get.pause()
        # 填充屏幕背景
        screen.blit(image_start_background, (0, 0))
        # 绘制游戏标题
        title_font = pygame.font.Font('title.ttf', 100)
        title_text = title_font.render("战争烈焰", True, (253, 68, 4))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 150))
        # 绘制开始按钮
        button_font = pygame.font.Font('msyh.ttf', 48)
        button_text1 = button_font.render("开始游戏", True, (255, 255, 255))
        button_rect1 = button_text1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2+20))
        pygame.draw.rect(screen, (0, 128, 0), button_rect1, border_radius=10)
        screen.blit(button_text1, button_rect1)
        # 绘制退出按钮
        button_text2 = button_font.render("退出游戏", True, (255, 255, 255))
        button_rect2 = button_text2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 110))
        pygame.draw.rect(screen, (128,0, 0), button_rect2, border_radius=10)  # 红色矩形表示退出
        screen.blit(button_text2, button_rect2)
        #燃烧特效
        image_fire=pygame.image.load("image/fire.png")
        screen.blit(image_fire,(screen.get_width() // 2 - title_text.get_width() // 2, 150))
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect1.collidepoint(event.pos):
                    running = True
                    sound_start.play(0)
                    time.sleep(1.5)
                    start = False  # 点击开始按钮后退出开始界面
                elif button_rect2.collidepoint(event.pos):
                    pygame.quit()
        pygame.display.flip()

    while running:
        if victory == -1:
            sound_all_get.unpause()

        #############初始化部分1
        start_time = time.time()#记录开始时间
        #背景的始终刷新
        screen.blit(image_background, (0, 0))
        part_runway = image_runway.subsurface((0, start_image, 252, end_image))  # 仅仅截取完整图片的其中的一部分
        part_runway = pygame.transform.scale(part_runway, (240, 720))
        screen.blit(part_runway, (115, 0))
        if end_image >745:
            start_image -=5
            end_image -=5
        else:
            end_image = 760
            start_image=40



    ##############玩家部分

        # 持续获取各种输入事件,用于控制玩家的移动
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 如果按了右上角的退出键
                running = False
                is_over = False
                #如果按了上下左右键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    Player.left(player)
                if event.key == pygame.K_d:
                    Player.right(player)
                if event.key == pygame.K_w:
                    Player.up(player)
                if event.key == pygame.K_s:
                    player.down()



            #如果释放了某个键
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                        Player.left_up(player)
                if event.key == pygame.K_d:
                        Player.right_up(player)
                if event.key == pygame.K_w:
                        Player.up_up(player)
                if event.key == pygame.K_s:
                        player.down_up()

        # 根据change变量的变化，让玩家xy数据更新，并且绘制在屏幕上
        player.update()
        player.draw(screen,ifOpen)
        #BOSS在下方

        # 血条绘制-玩家
        text = font.render('HP:', True, (255, 0, 0))  # 获取文本的矩形对象，并设置其在左上角
        screen.blit(text, text.get_rect(topleft=(0, 80)))
        if hitPoint >= 0:
            part_hitPoint = image_hitPoint.subsurface((0, 0, hitPoint, 20))
        else:
            # 退出循环,播放死亡结局
            part_hitPoint = image_hitPoint.subsurface((0, 0, 0, 20))
            victory=0
        screen.blit(part_hitPoint, (0, 100))

        # 护盾值绘制-玩家
        text = font.render('DP:', True, (180, 0, 255))  # 获取文本的矩形对象，并设置其在左上角
        screen.blit(text, text.get_rect(topleft=(0, 125)))
        part_defence = image_defencePoint.subsurface((0, 0, defencePoint, 20))
        screen.blit(part_defence, (0, 145))

        if defencePoint < 100:
            defencePoint += 0.5  # 每秒钟护盾值回复0.5
        elif defencePoint >= 100:
            ifOpen = 1  # 如果护盾值积累满100了，回复保护，但是不会超过100
            defencePoint = 100



    ###########障碍物部分

        #障碍物-轮胎生成，加个计时装置，固定运行多少时间(玩家/障碍大概移动5-10格像素/帧)，就加一个障碍物
        current_time = time.time()
        accumulator_obstacle += (current_time - start_time)*10  # 根据时间增加accumulator,单位（秒）

        # 障碍物生成-轮胎
        if accumulator_obstacle >= 3:#三秒固定生成一个障碍物
                obstacle_tire_all.append(Obstacle_tire())
                # 随机性，概率生成2-3个障碍物
                if random.randint(1, 2) == 1:
                    obstacle_tire_all.append(Obstacle_tire())
                if random.randint(1, 4) == 1:
                    obstacle_tire_all.append(Obstacle_tire())

                 #重新记录
                accumulator_obstacle=0

        #具体更新每一个障碍物的状态
        for obstacle_now in obstacle_tire_all:
            # 更新障碍物的数据，并且会持续向下移动
            obstacle_now.update()
            #如果越界了，就删除这个障碍物
            if obstacle_now.is_off()==1:
                obstacle_tire_all.remove(obstacle_now)
            else:
                #判断玩家有没有撞上这个障碍物
                if obstacle_now.collision(player.output_place())==1:
                    if ifOpen==0:
                        hitPoint-=10 #没有护盾情况下，遇到障碍物，玩家生命值-10
                    elif ifOpen==1:
                        hitPoint-=1 #有护盾的情况下，遇到障碍物，玩家生命值-1，护盾能力值-75
                        defencePoint-=75
                        if defencePoint<=0:#护盾值小于0了，就破防，光环消失
                            defencePoint=0
                            ifOpen=0
                # 绘制到画面上
                obstacle_now.draw(screen)

        # 障碍物生成-炸弹
        accumulator_obstacle_bomb += 0.5
        if accumulator_obstacle_bomb >= 30:#60帧固定生成一个障碍物-炸弹
                obstacle_bomb_all.append(Obstacle_bomb())
                 #重新记录
                accumulator_obstacle_bomb=0
        if random.randint(1, 400) == 1:#低概率立刻暴雷
            obstacle_bomb_all.append(Obstacle_bomb())

        #具体更新每一个障碍物-炸弹的状态
        for obstacle_now in obstacle_bomb_all:
            # 更新障碍物的数据，并且会持续向下移动
            obstacle_now.update()
            #如果越界了，就删除这个障碍物
            if obstacle_now.is_off()==1:
                obstacle_bomb_all.remove(obstacle_now)
            else:
                #判断玩家有没有撞上这个障碍物
                if obstacle_now.collision(player.output_place())==1:
                    obstacle_bomb_all.remove(obstacle_now)
                    if victory == -1:
                        sound_bomb_get = sound_bomb.play(0)
                    if ifOpen==0:
                        hitPoint-=20 #没有护盾情况下，遇到障碍物-炸弹，玩家生命值-20
                    elif ifOpen==1:
                        hitPoint-=1 #有护盾的情况下，遇到障碍物-炸弹，玩家生命值-1，护盾能力值-120
                        defencePoint-=120
                        if defencePoint<=0:#护盾值小于0了，就破防，光环消失
                            defencePoint=0
                            ifOpen=0
                # 绘制到画面上
                else:
                    obstacle_now.draw(screen)

        ###########道具部分

        #道具生成-治疗
        accumulator_heal += 0.5
        if accumulator_heal >= 350:  # 600帧概率生成一个治疗
            if random.randint(1, 40) == 1:
                prop_heal_all.append(Prop_heal())
                # 重新记录
                accumulator_heal = 0
        #道具生成-护盾
        accumulator_shield += 0.5
        if accumulator_shield >= 300:
            if random.randint(1, 30) == 1:
                prop_shield_all.append(Prop_shield())
                accumulator_shield = 0
        #道具生成-闪电
        accumulator_lightning += 0.5
        if accumulator_lightning >= 500:
            if random.randint(1, 50) == 1:
                prop_lightning_all.append(Prop_lightning())
                accumulator_lightning = 0


        # 具体更新每一个道具-治疗的状态
        for prop_now in prop_heal_all:
            # 更新障碍物的数据，并且会持续向下移动
            prop_now.update()
            # 如果越界了，就删除这个障碍物
            if prop_now.is_off() == 1:
                prop_heal_all.remove(prop_now)
            else:
                # 判断玩家有没有撞上这个治疗
                if prop_now.collision(player.output_place()) == 1:
                    prop_heal_all.remove(prop_now)
                    hitPoint = min(100,hitPoint+20)
                # 绘制到画面上
                else:
                    prop_now.draw(screen)

        # 具体更新每一个道具-护盾的状态
        for prop_now in prop_shield_all:
            # 更新障碍物的数据，并且会持续向下移动
            prop_now.update()
            # 如果越界了，就删除这个障碍物
            if prop_now.is_off() == 1:
                prop_shield_all.remove(prop_now)
            else:
                # 判断玩家有没有撞上这个护盾
                if prop_now.collision(player.output_place()) == 1:
                    prop_shield_all.remove(prop_now)
                    defencePoint = min(100,defencePoint+50)
                else:
                    prop_now.draw(screen)
         #具体更新每一个道具-闪电的状态
        for prop_now in prop_lightning_all:
            # 更新障碍物的数据，并且会持续向下移动
            prop_now.update()
            # 如果越界了，就删除这个障碍物
            if prop_now.is_off() == 1:
                prop_lightning_all.remove(prop_now)
            else:
                # 判断玩家有没有撞上这个闪电
                if prop_now.collision(player.output_place()) == 1:
                    lightning_image = pygame.image.load("image/lightning.png")
                    prop_lightning_all.remove(prop_now)
                    lightning_time=6
                    # 更新屏幕显示
                    pygame.display.update()
                    if victory == -1:
                        sound_lightning.play(0)


                else:
                    prop_now.draw(screen)



        ################子弹部分

        #子弹生成，也计时，但是要比障碍物快
        if accumulator_shell>2:
            accumulator_shell=0
        else:
            accumulator_shell+=1

        #生成每一个子弹
        if accumulator_shell==0:
            shell_player.append(shell(player.output_place()))

        #更新每一个子弹的状态
        for shell_now in shell_player:
            # 更新障碍物的数据，并且会持续向下移动
            shell_now.update()
            # 如果越界了，就删除这个子弹
            if shell_now.is_off() == 1:
                shell_player.remove(shell_now)
            else:
                # 判断BOSS有没有撞上这个子弹，撞上了播放爆炸效果，并且移除
                if shell_now.collision(Boss.output_place()) == 1:
                    hitPoint2 -= 1#这个类似于子弹伤害
                    shell_player.remove(shell_now)
                # 正常绘制到画面上
                else:
                    shell_now.draw(screen)



        ###########Boss部分
        Boss.draw(screen)

        # 血条绘制-BOSS
        text = font.render('BOSS:', True, (255, 0, 0))  # 获取文本的矩形对象，并设置其在左上角
        text_rect = text.get_rect(topleft=(0, 680))
        screen.blit(text, text_rect)
        if hitPoint2>=0:
            part_hitPoint2 = image_hitPoint2.subsurface((0, 0, hitPoint2, 20))
        else:
            part_hitPoint2 = image_hitPoint2.subsurface((0, 0, 0, 20))
            #跳出循环，胜利动画
            victory=1
        screen.blit(part_hitPoint2, (0, 700))

        if lightning_time>0:
            hitPoint2 -= 5
            (now_x1, now_y1), (now_x2, now_y2) = player.output_place()
            # 计算闪电图像应该加载的位置（底部对齐）
            lightning_y = now_y2 - lightning_image.get_height()
            screen.blit(lightning_image, (now_x1, lightning_y-20))
            lightning_time-=1
        ################结局部分#############

        if victory == 1:  # 如果玩家胜利
            image_victory = pygame.transform.scale(pygame.image.load("image/end_victory.png"), (450, 720))
            screen.blit(image_victory, (0, 0))
            #bgm暂停
            sound_all_get.pause()
            #胜利音频播放
            sound_win_get.unpause()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:#扣1复活
                        running = False
                        sound_win_get.pause()
                    else:
                        sound_win_get.pause()
                        start = True
                        running = False
        elif victory==0:  # 如果玩家死亡
            image_fail = pygame.transform.scale(pygame.image.load("image/end_fail.png"), (450, 720))
            screen.blit(image_fail, (0, 0))
            # bgm暂停
            sound_all_get.pause()
            # 失败音频播放
            sound_lose_get.unpause()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:#扣1复活
                        running = False
                        sound_lose_get.pause()
                    else:
                        start = True
                        running = False
                        sound_lose_get.pause()



        #########其他部分
        # 将screen变量里改变的内容显示到游戏窗口上
        pygame.display.flip()

        # 限制游戏运行速度，控制一帧为30ms，如果不足就补齐，30为常规
        clock.tick(30)



