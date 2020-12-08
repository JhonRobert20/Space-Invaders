import pygame
import os
import time 
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("SPACE INVADERS")

#Load images [ship, laser]
Red_Space_Ship = pygame.image.load(os.path.join("assets","pixil_ship_red.png"))
Red_Laser = pygame.image.load(os.path.join("assets","pixil_laser_red.png"))

Green_Space_Ship = pygame.image.load(os.path.join("assets","pixil_ship_green.png"))
Green_Laser = pygame.image.load(os.path.join("assets","pixil_laser_green.png"))

Blue_Space_Ship = pygame.image.load(os.path.join("assets","pixil_ship_blue.png"))
Blue_Laser = pygame.image.load(os.path.join("assets","pixil_laser_blue.png"))

#Player player
Yellow_Space_Ship = pygame.image.load(os.path.join("assets","pixil_ship_player.png"))#
Yellow_Laser = pygame.image.load(os.path.join("assets","pixil_laser_player.png"))#


#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y +=velocity

    def off_screen(self, height):
        return  not(self.y <=height and self.y >= 0)

    def  collision(self, obj):
        return collide(obj, self)


class Ship:
    COOLDOWN = 30
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.down_counter = 0

    def draw(self,window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def cooldown(self):
        if self.down_counter >= self.COOLDOWN:
            self.down_counter = 0
        elif self.down_counter > 0:
            self.down_counter += 1

    def shoot(self):
        if self.down_counter ==0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.down_counter = 1

    def get_height(self):
        return self.ship_img.get_height()
    def get_width(self):
        return self.ship_img.get_width()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Yellow_Space_Ship
        self.laser_img = Yellow_Laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() +10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() +10, self.ship_img.get_width() * ((self.health)/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "RED":(Red_Space_Ship, Red_Laser),
                "GREEN":(Green_Space_Ship, Green_Laser),
                "BLUE":(Blue_Space_Ship, Blue_Laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x,y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self,velocity):
        self.y += velocity 
    
    def shoot(self):

        aditional_x = 0
        aditional_y = 0

        if self.down_counter ==0:
            

            if self.ship_img == self.COLOR_MAP["RED"][0]:
                aditional_x = +17
                aditional_y = 54

            if self.ship_img == self.COLOR_MAP["BLUE"][0]:
                aditional_x = -8
                aditional_y = +20
            
            if self.ship_img == self.COLOR_MAP["GREEN"][0]:
                aditional_x = 7
                aditional_y = 22

            laser = Laser(self.x + aditional_x, self.y + aditional_y, self.laser_img)
            self.lasers.append(laser)
            self.down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) !=None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 10
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)

    enemy_vel = 5
    enemis = []
    wave_length = 5

    laser_vel = 6
    player_vel = 5
    player = Player(10, 200)
    
    Lost = False
    lost_count = 0

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0,0))
        #draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,0,0))
        WIN.blit(lives_label, (10, 10))        
        WIN.blit(level_label, (WIDTH-level_label.get_width()-10, 10))

        if Lost:
            lost_label = lost_font.render("YOU LOST", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        for enemi in enemis:
            enemi.draw(WIN)

        player.draw(WIN)
        
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            Lost = True
            lost_count +=1
        
        if Lost:
            if lost_count >= FPS * 3:
                run = False
                lost_count = 0
            else:
                continue
            
        if len(enemis) == 0:
            level +=1
            wave_length +=5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,WIDTH-50),random.randrange(-1500, -1000),random.choice(["RED", "BLUE", "GREEN"]))##Desde donde-1500,1000 /"RED","BLUE","GREEN"
                enemis.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and (player.x - player_vel +13> 0 ):#Left
            player.x -= player_vel
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and (player.x + player_vel + player.get_width()< WIDTH):#Right
            player.x += player_vel
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and (player.y - player_vel > 0 ):#Up
            player.y -= player_vel
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and (player.y + player_vel + player.get_height()< HEIGHT):#Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemi in enemis[:]:
            enemi.move(enemy_vel)
            enemi.move_lasers(laser_vel, player)
            if random.randrange(0, 240) == 1:
                enemi .shoot()
            
            if collide(enemi, player):
                player.health -= 10
                enemis.remove(enemi)

            elif (enemi.y+ enemi.get_height()) > HEIGHT and(lives > 0) :
                lives -=1
                enemis.remove(enemi)
        player.move_lasers(-laser_vel, enemis)
        
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run: 
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 -title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
    
main_menu()