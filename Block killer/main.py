import sys
import os
import random
import pygame
from pygame.locals import *


class Time_record():
    def __init__(self, time):
        self.time = time
        self.init = time
    def time_over(self):
        self.time -= 1
        if self.time == 0:
            self.time = self.init
            return True
    def print_time(self): 
        print(self.time)


class Particle_set():
    def __init__(self, textrue, point, block_size):
        image = pygame.image.load('assets/'+textrue).convert_alpha()
        size = 1/random.randint(8, 16)*block_size
        self.image = pygame.transform.scale(image, (size, size)).convert_alpha()
        self.point = point
        self.block_size = block_size
        self.rect = self.image.get_rect()
        self.rect.x = self.point[0]*self.block_size + self.block_size/2
        self.rect.y = self.point[1]*self.block_size + random.randint(0, block_size)

        self.speed = random.randint(-10, 10)
        self.down_speed = random.randint(-10, -5)
        self.t = 0
    def play(self, screen, screen_size):
        screen.blit(self.image, self.rect)
        self.rect.x += self.speed
        self.rect.y += self.down_speed
        self.t += 1
        self.down_speed = self.down_speed+1*self.t
        if self.rect.y >= screen_size[1]:
            return True


def block_texture_get(block_size, textures_list):
    files = os.walk('assets')
    for each_file in files:
        textures_list = each_file[2]
    index = random.randint(0, len(textures_list)-1)
    texture = pygame.image.load('assets/'+textures_list[index])
    texture = pygame.transform.scale(texture, (block_size,block_size))
    return textures_list[index]

def block_position_get(block_size, screen_size):
    x_max = screen_size[0] // block_size - 1
    y_max = screen_size[1] // block_size
    x = random.randint(0,x_max)
    y = 0
    return [x, y]

def run(screen, texture, point, block_size, screen_size, time, filled_point):
    position = [point[0]*block_size, point[1]*block_size]
    image = pygame.transform.scale(pygame.image.load('assets/'+texture), (block_size, block_size))
    screen.blit(image, position)
    block_pos = point
    check_bottom = [block_pos[0], block_pos[1]+1]
    #方块下落
    if position[1]+block_size < screen_size[1] and check_bottom not in filled_point:
        if time.time_over():
            point[1] += 1
    elif position[1]+block_size >= screen_size[1] or check_bottom in filled_point:
        return True

#方块移动
def turn(if_left, if_right, if_down, block_left, block_right, block_bottom,\
         point, block_size, screen_size, time, filled_point):
    if if_left == True and time.time_over():
        if point[0] > 0 and block_left not in filled_point:
            point[0] -= 1
    if if_right == True and time.time_over():
        if point[0] < screen_size[0]/block_size-1 and block_right not in filled_point:
            point[0] += 1
    if if_down == True and time.time_over():
        if point[1] < screen_size[1]/block_size-1 and block_bottom not in filled_point:    
            point[1] += 1

#填充显示和消除以及游戏失败判断
def fill_show(fill_list, filled_point, screen, block_size):
    if fill_list != []:
        a = 0
        list1 = []
        kill_blocks_point = []
        for each in fill_list:
            image =pygame.image.load('assets/'+each[4]).convert_alpha()
            image = pygame.transform.scale(image, (block_size, block_size)).convert_alpha()
            screen.blit(image, (each[0], each[1]))
            if [each[2], each[3]] not in filled_point:
                filled_point.append([each[2], each[3]]) #([方块位于点阵上的x坐标, 方块位于点阵上的y坐标])
            #检测每一个方块的四周并进行消除操作
            each_left = [each[0]-block_size, each[1], each[2]-1, each[3], each[4]]
            each_right = [each[0]+block_size, each[1], each[2]+1, each[3], each[4]]
            each_top = [each[0], each[1]-block_size, each[2], each[3]-1, each[4]]
            each_bottom = [each[0], each[1]+block_size, each[2], each[3]+1, each[4]]
            if each_left in fill_list:
                a += 1
                list1.append(each_left)
            if each_right in fill_list:
                a += 1
                list1.append(each_right)
            if each_top in fill_list:
                a += 1
                list1.append(each_top)
            if each_bottom in fill_list:
                a += 1
                list1.append(each_bottom)
            if a >= 2:
                for x in list1:
                    point = [x[2], x[3]]
                    fill_list.remove(x)
                    if point in filled_point:
                        filled_point.remove(point)
                    kill_blocks_point.append(point)
                fill_list.remove(each)
                filled_point.remove([each[2], each[3]])
                kill_blocks_point.append([each[2], each[3]])
                return [kill_blocks_point, each[4]] #[[[x,y], [x,y], [x,y], ...], texture]
            else:
                list1.clear()
            a = 0

        #游戏失败判断
        for each_point in filled_point:
            if each_point[1] <= 0:
                return True

def main():
    pygame.font.init()
    font1 = pygame.font.Font('effect/block_font.ttf', size=50)
    font2 = pygame.font.Font('effect/block_font.ttf', size=60)
    font3 = pygame.font.Font('effect/block_font.ttf', size=90)
    score = 0
    block_size = 64
    screen_size = (block_size*12, block_size*15)
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    block_texture = None
    running = 'guide_mode'
    turn_left = False
    turn_right = False
    turn_down = False
    freeze = False
    point = [0,0]
    fill_list = []
    filled_point = []
    textures = []
    particles = []
    guide_particles = []
    time1 = Time_record(15)   #下落延迟
    time2 = Time_record(4)    #移动延迟
    time3 = 150  #冰冻时间
    init_time3 = time3
    fps = 60

    #初始化效果界面
    frozen = pygame.image.load('effect/frozen.png')
    frozen = pygame.transform.scale(frozen, (screen_size[0], screen_size[1]))
    #初始化方块材质和位置
    block_texture = block_texture_get(block_size=block_size, textures_list=textures)
    point = block_position_get(block_size=block_size, screen_size=screen_size)
    #检查方块周边
    check_left = [point[0]-1, point[1]]
    check_right = [point[0]+1, point[1]]
    check_bom = [point[0], point[1]+1]

    y = -10
    welcome_text_y = -250
    while True:
        if running == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            text = 'score:'+str(score)
            score_text = font1.render(text, True, 'white')
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                turn_left = True
            else:
                turn_left = False
            if keys[pygame.K_RIGHT]:
                turn_right = True
            else:
                turn_right = False
            if keys[pygame.K_DOWN]:
                turn_down = True
            else:
                turn_down = False

            screen.fill('black')

            if run(screen=screen, texture=block_texture, point=point,\
            block_size=block_size, screen_size=screen_size, time=time1, filled_point=filled_point):
                image = pygame.image.load('assets/'+block_texture).convert_alpha()
                image = pygame.transform.scale(image, (block_size, block_size)).convert_alpha()
                block_rect = image.get_rect()
                block_rect.x = point[0]*block_size
                block_rect.y = point[1]*block_size
                fill_list.append([block_rect.x,block_rect.y, point[0],point[1], block_texture])
                                #([方块实时x坐标位置,方块实时y坐标位置, 方块位于点阵上的x坐标,方块位于点阵上的y坐标, 方块材质名称)

                #刷新下一方块的属性
                block_texture = block_texture_get(block_size=block_size, textures_list=textures)
                point = block_position_get(block_size=block_size,screen_size=screen_size)

            var = fill_show(fill_list=fill_list, filled_point=filled_point, screen=screen, block_size=block_size)
            if var is not None and var != True:
                particles_point = var[0]
                for each in particles_point:
                    score += 10
                    for i in range(64):
                        particle = Particle_set(textrue=var[1], point=each, block_size=block_size)
                        particles.append(particle)

                if var[1] == 'ice.png':
                    freeze = True
                if var[1] == 'tnt_side.png':
                    pass

                var.clear()
            elif var == True:
                running = False

            if freeze:
                fps = 30
                screen.blit(frozen, (0, 0))
                freeze_text = font2.render('FORZEN TIME '+str(time3//fps+1), True, (200,200,255))
                screen.blit(freeze_text, (screen_size[0]//3, 80))
                time3 -= 1
                if time3 == 0:
                    fps = 60
                    time3 = init_time3
                    freeze = False

            if particles != []:
                for each_particle in particles:
                    close = each_particle.play(screen=screen, screen_size=screen_size)
                    if close:
                        particles.remove(each_particle)

            #更新方块周边状态
            check_left = [point[0]-1, point[1]]
            check_right = [point[0]+1, point[1]]
            check_bom = [point[0], point[1]+1]

            #实现方块移动
            turn(if_left=turn_left,if_right=turn_right,if_down=turn_down,point=point,block_size=block_size,\
                screen_size=screen_size,time=time2,filled_point=filled_point,block_left=check_left,\
                block_right=check_right, block_bottom=check_bom)

            screen.blit(score_text, (10, 10))
        if running == 'guide_mode':
            screen.fill('black')
            welcome_text = font3.render("BLOCK KILLER", True, 'white')
            welcome_text_back = font3.render("BLOCK KILLER", True, (100,100,100))
            author_text = font1.render('make by WH12520', True, 'white')
            start_text = font1.render('press any key to start', True, 'yellow', (0,150,0))
            guide_image = pygame.image.load('assets/diamond_ore.png').convert_alpha()
            guide_image = pygame.transform.scale(guide_image, (block_size,block_size)).convert_alpha()
            guide_image2 = pygame.image.load('assets/dirt.png').convert_alpha()
            guide_image2 = pygame.transform.scale(guide_image2, (block_size,block_size)).convert_alpha()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    fill_list.clear()
                    filled_point.clear()
                    running = True
            if welcome_text_y <= screen_size[1]//20:
                welcome_text_y += 10
            else:
                screen.blit(guide_image2, (5*block_size, screen_size[1]-block_size))
                screen.blit(guide_image2, (6*block_size, screen_size[1]-block_size))
                y += 0.1
                if y*block_size >= screen_size[1]-block_size:
                    for i in range(3):
                        the_point = [7+i, y-1]
                        for i in range(64):
                            guide_particle = Particle_set(textrue='diamond_ore.png',\
                                                        point=the_point,\
                                                        block_size=block_size)
                            guide_particles.append(guide_particle)
                    y = -10
                else:
                    screen.blit(guide_image, (7*block_size, screen_size[1]-block_size))
                    screen.blit(guide_image, (8*block_size, y*block_size))
                    screen.blit(guide_image, (9*block_size, screen_size[1]-block_size))
                screen.blit(start_text, (screen_size[0]//3.95, welcome_text_y+80))
                screen.blit(author_text, (screen_size[0]//3, screen_size[1]-100))
            screen.blit(welcome_text_back, (screen_size[0]//3.75-5, welcome_text_y-5))
            screen.blit(welcome_text, (screen_size[0]//3.75, welcome_text_y))
            if guide_particles != []:
                for each in guide_particles:
                    if each.play(screen=screen, screen_size=screen_size):
                        guide_particles.remove(each)
        if running == False:
            screen.fill('black')
            over_text1 = font3.render("GAME OVER", True, 'white')
            over_text2 = font1.render("press any key to restart", True, 'yellow', (0,150,0))
            over_text3 = font2.render("your score: "+str(score), True, 'white')
            screen.blit(over_text1, (screen_size[0]//3, screen_size[1]//3))
            screen.blit(over_text2, (screen_size[0]//3-60, screen_size[1]//1.5))
            screen.blit(over_text3, (screen_size[0]//3, screen_size[1]//3+100))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    fill_list.clear()
                    filled_point.clear()
                    score = 0
                    running = True

        pygame.display.flip()
        clock.tick(fps)

main()