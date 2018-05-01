
# coding: utf-8

# In[549]:

#! /usr/bin/python

import pygame
import math as m
from pygame import *
import random


WIN_WIDTH = 1024
WIN_HEIGHT = 576
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LGREEN = (60, 225, 60)
GREEN = (0, 255, 0)
DARKGR = (14, 122, 16)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (100, 100, 100)
LGREY =(150, 150, 150)
DGREY =(50, 50,50)
SLATE = (30, 107, 122)
GOLD = (249, 238, 74)
PURPLE = (153, 4, 216)
PINK = (247, 128, 128)
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = HWSURFACE|DOUBLEBUF
CAMERA_SLACK = 50
TILE_SIZE = 16
ROOM_SIZE = [512,288]


# In[550]:

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, (height+100))
        #level width and height are passed into camera object

    def apply(self, target):
        return target.rect.move(self.state.topleft) #apply is used when blitting entities and things

    def update(self, target):
        #set camera state equal to 
        self.state = self.camera_func(self.state, target.rect) #runs "complex cam

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+256, -t+144, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-512), l)   # stop scrolling at the right edge
    t = max(-(camera.height-288), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)


# In[551]:

class Map(object):
    def __init__(self, player):
        
        self.player = player
        self.w = 8
        self.h = 5       
        self.currentx = 0
        self.currenty = 0
        #self.globalcoordinatex = self.player.rect.x+ (self.level.x*512)
        #self.globalcoordinatey = self.player.rect.y+(self.level.y*288)
        self.gen_mapgrid()
        self.switch_level(160, 96)
        self.dString  = ""
        
    def gen_mapgrid(self):
        self.grid = [[0 for x in range(self.w)] for y in range(self.h)]
        counter = 0
        counter2 = 0
        #self.get_player_coordinates()
        for level in (Level_01(self.player), Level_02(self.player), Level_03(self.player), Level_04(self.player)):
            
            for coord in level.mapcoordinates:
                
                
                print(coord)
                self.grid[coord[1]][coord[0]] = 1
    def get_player_coordinates(self):
        self.globalcoordinatex = self.player.rect.x + self.level.x*ROOM_SIZE[0]
        self.globalcoordinatey = self.player.rect.y + self.level.y*ROOM_SIZE[1]
        self.get_map_coordinates()
    def get_map_coordinates(self):
        
        self.mapx = self.globalcoordinatex//ROOM_SIZE[0]
        self.mapy = self.globalcoordinatey//ROOM_SIZE[1]
        self.mapco = [self.mapx, self.mapy]
        
        
    def switch_level(self, newx, newy):
        self.globalcoordinatex = newx
        self.globalcoordinatey = newy
        self.get_map_coordinates()
        if (self.mapco == [0,0]) or (self.mapco == [0,1]) or (self.mapco ==[0,2]):
            self.level = Level_01(self.player)
           # self.player.rect.x = self.globalcoordinatex - self.level.x*512
           # self.player.rect.y = self.globalcoordinatey - self.level.y*288
            print('level 1')
        elif (self.mapco == [1,2]) or (self.mapco == [1,3]) or (self.mapco == [2,2]) or (self.mapco == [2,3]):
            self.level = Level_02(self.player)
            print('level 2')
            #self.player.rect.x = self.globalcoordinatex - self.level.x*512
            #self.player.rect.y = self.globalcoordinatey - self.level.y*288
            
        elif (self.mapco == [3,3]) or (self.mapco == [3,4]):
            self.level = Level_03(self.player)
            print('level 3')
            #self.player.rect.x = self.globalcoordinatex - self.level.x*512
            #self.player.rect.y = self.globalcoordinatey - self.level.y*288

        elif (self.mapco == [4,4]):
            self.level = Level_04(self.player)
            
            #self.player.rect.x = self.globalcoordinatex - self.level.x*512
            #self.player.rect.y = self.globalcoordinatey - self.level.y*288

        else:
            self.level = Level_01(self.player)
            
        #self.level = 
   


# In[552]:

class Level(object):
    def __init__(self, player):
        self.player = player
        # instantiate sprite groups
        self.entities = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.teleX = 0
        self.teleY = 0
        self.platforms = []
        self.intplatforms = pygame.sprite.Group()
        self.invisiblocks = []
        self.particles = pygame.sprite.Group()
        self.generators = pygame.sprite.Group()
        self.overlays = pygame.sprite.Group()
        self.underlays = pygame.sprite.Group()
        self.soundlist = []
        bullet_sound = pygame.mixer.Sound("bullet.wav")
        self.soundlist.append(bullet_sound)
        
        #self.entrypoints = []
    def layer2_build(self):
        x=y=0
        for row in self.overlaymat:
            for col in row:
                if col == "P":
                    p = GroundCover(x,y, 'center')
                    self.overlays.add(p)
                if col == "R":
                    r = GroundCover(x,y,'right')
                    self.overlays.add(r)
                if col =="L":
                    l = GroundCover(x,y,'left')
                    self.overlays.add(l)
                if col == "S":
                    s = ParticleGenerator(self, x,y,5)
                    self.generators.add(s)
                x += TILE_SIZE
            y += TILE_SIZE
            x = 0
    def layer0_build(self):
        x=y=0
        for row in self.underlaymat:
            for col in row:
                if col == "S":
                    s = ParticleGenerator(self, x,y, 5)
                    self.generators.add(s)
                x += TILE_SIZE
            y += TILE_SIZE
            x = 0
    def level_build(self):
        x=y=0
        for row in self.level:
            for col in row:
                if col == "W":
                    w = Water(x,y)
                    self.overlays.add(w)
               # if col == "R":
                #    r = ParticleGenerator(self, x, y)
                #    self.generators.add(r)
                if col == "P":
                    p = Platform(x, y)
                    self.platforms.append(p)
                    self.entities.add(p)
                if col == "A":
                    a = GradientPlatform(x, y, 0)
                    self.platforms.append(a)
                    self.entities.add(a)
                if col == "B":
                    b = GradientPlatform(x, y, 1)
                    self.platforms.append(b)
                    self.entities.add(b)
                if col == "C":
                    c = GradientPlatform(x, y, 2)
                    self.platforms.append(c)
                    self.entities.add(c)
                if col == "G":
                    self.goopSpawn(x,y)
                if col == "U":
                    u = SpikeBlock(x,y)
                    self.platforms.append(u)
                    self.entities.add(u)
                if col == "F":
                    f = StoneFace(x,y)
                    self.intplatforms.add(f)
                    self.platforms.append(f)
                    self.entities.add(f)
                if col == "@":
                    i = InvisiBlock(x,y)
                    self.invisiblocks.append(i)
                if col == "D":
                    d  = DestBlock(x,y)
                    self.platforms.append(d)
                    self.entities.add(d)
                if col == "Z":
                    z = DoubleJump(self, x,y)
                    self.pickups.add(z)
                    #self.entities.add(z)
                if col == "T":
                    t = Gem(x,y, True) ##no horiz flip
                    self.entities.add(t)
                if col == "L":
                    t = Gem(x,y, False) # horiz flip
                    self.entities.add(t)
                    
                x += TILE_SIZE
            y += TILE_SIZE
            x = 0
        self.total_level_width  = len(self.level[0])*TILE_SIZE
        self.total_level_height = len(self.level)*TILE_SIZE
        self.boundingbox = Rect(0,0, self.total_level_width+TILE_SIZE, self.total_level_height+TILE_SIZE)
    def goopSpawn(self, x, y):
        enemy = Goop(self, x, y)
        self.enemies.add(enemy)
        self.entities.add(enemy)
    def H_pickupSpawn(self, x, y):
        pick = HealthPickup(self,x,y)
        self.pickups.add(pick)


# In[553]:

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


# In[554]:

class Particle(Entity):
    def __init__(self, level, x, y, func):
        super().__init__()
        self.rect = Rect(x, y, 1, 1)        
        self.image = Surface((1,1))
        self.image.fill(Color("#ffffff"))
        self.counter= 0
        self.level = level
        self.level.particles.add(self)
        self.move = func
        
        self.energy = random.randint(1, 20) 
        self.energyscale = 6
        self.duration = 200
        self.period = 4
        #rectangular coordinates, used for blitting
        self.xAccel = 0
        self.yAccel = 0
        self.xvel = 0 #store current velocity
        self.yvel = 0 
        self.xinit = x #store inital position
        self.yinit = y 
        #now defining the terms in polar coordinates:
        #radial position, velocity, and acceleration. useful for orbital equations
        self.r = 0
        self.rdot = 0
        sefl.rdotdot = 0
        
        #polar position, velocity, and accel
        self.theta = 0
        self.omega = 0
        self.alpha = 0
        
        
        
        if self.move == 3 or self.move == 5:
            if self.energy == 1:
                self.image.fill(Color("#3678e2"))
            if self.energy == 2:
                self.image.fill(Color("#4d87e6"))
            if self.energy == 3:
                self.image.fill(Color("#6396e9"))
            if self.energy == 4:
                self.image.fill(Color("#79a5ec"))
            if self.energy == 5:
                self.image.fill(Color("#8fb4ef"))
            if self.energy == 6:
                self.image.fill(Color("#a6c3f2"))
            if self.energy == 7:
                self.image.fill(Color("#bcd2f5"))
            if self.energy == 8:
                self.image.fill(Color("#d2e1f9"))
            if self.energy == 9:
                self.image.fill(Color("#e9f0fc"))
            if self.energy == 10:
                self.image.fill(Color("#ffffff"))
    def color_change(self):
        if self.move == 4 or self.move == 5:
            if self.counter<(self.duration):
                if self.counter == 10:
                    self.image.fill(Color("#e9f0fc"))
                if self.counter == 20:
                    self.image.fill(Color("#d2e1f9"))
                if self.counter == 30:
                    self.image.fill(Color("#bcd2f5"))
                if self.counter == 40:
                    self.image.fill(Color("#a6c3f2"))
                if self.counter == 50:
                    self.image.fill(Color("#8fb4ef"))
                if self.counter == 60:
                    self.image.fill(Color("#79a5ec"))
                if self.counter == 70:
                    self.image.fill(Color("#6396e9"))
                if self.counter == 80:
                    self.image.fill(Color("#4d87e6"))
                if self.counter == 90:
                    self.image.fill(Color("#3678e2"))
                
            
    def movement(self):
        if self.move == 1:
            #straight up at slow pace
            if self.counter < self.duration:
                if self.counter % self.period == 0:
                    self.rect.y += -1
            
            else:
                self.level.particles.remove(self)
            self.counter +=1
        elif self.move == 2:
            #sinusoidal x movement
            if self.counter < self.duration:
                
                if self.counter % self.period == 0:
                    self.rect.y -= 1
                    self.rect.x = self.xinit +(self.energy*self.energyscale*m.sin(self.energy*(self.rect.y-self.yinit)))
                    
            
        elif self.move == 3:
            #sinusoidal x movement
            if self.counter < self.duration:
                
                if self.counter % self.period == 0:
                    self.rect.y -= 1
                    self.rect.x = self.xinit +(self.energy*self.energyscale*m.sin(self.energy*(self.rect.y-self.yinit)))
                    
            
            else:
                self.level.particles.remove(self)
            self.counter +=1
        elif self.move == 4:
            if self.counter<(self.duration):
                
                if self.counter % self.period == 0:
                    self.rect.y -= 1
                    self.rect.x = self.xinit + (self.energy*self.energyscale*m.sin(self.energy*(self.rect.y-self.yinit)))
            else:
                self.level.particles.remove(self)
            self.counter +=1
        elif self.move == 5:
            if self.counter<(self.duration):
                xoffset = self.energyscale * self.energy * m.cos((self.counter*self.energy)/10)
                yoffset = self.energyscale * self.energy * m.sin((self.counter*self.energy)/10)
                self.rect.x = self.xinit + xoffset
                self.rect.y = self.yinit + yoffset 
            else:
                self.level.particles.remove(self)
            self.counter +=1
        elif self.move == 6:
            if self.counter<(self.duration): 
                #set random starting position
                initialxpos = xinit + random.randint(-20, 20)
                initialypos = yinit + random.randint(-20, 20)
                #transform to polar
                self.r = m.sqrt(((xinit - initalxpos)**2)+((yinit-initialypos)**2))
                self.theta = m.atan((yinit-initialypos)/(xinit-initialxpos))
                #set random starting velocity
                self.xvel = random.randint(-8,8)
                self.yvel = random.randint(-8,8)
                #get n-t coordinates of velocity vector
                self.n = self.xvel*m.cos(self.theta) + self.yvel*m.sin(self.theta)
                self.t = 0
                
                
            else:
                self.level.particles.remove(self)
            self.counter +=1
    def update(self):
        self.color_change()
        self.movement()

        


# In[555]:

class ParticleGenerator(Entity):
    def __init__(self, level, x, y, partype):
        super().__init__()
        self.rect = Rect(x, y, 1, 1)
        self.counter = 0
        self.level = level
        self.partype = partype
    def update(self):
        #if ((self.counter % 2) == 0): 
            
        part = Particle(self.level, self.rect.x, self.rect.y, self.partype)
        self.counter +=1
        if self.counter > 200:
            self.counter = 0
        


# In[556]:

class Level_01(Level):
    

    def __init__(self, player):
        
        super().__init__(player)
        self.bg = Surface((TILE_SIZE,TILE_SIZE))
        self.bg.convert()
        self.bg.fill(Color("#000000"))
        self.x = 0
        self.y = 0
        self.name = 'level01'
        self.mapcoordinates = []
        self.mapcoordinates.append((0,0))
        self.mapcoordinates.append((0,1))
        self.mapcoordinates.append((0,2))
        
        #self.entrypoints.append((80,80))
        #self.entrypoints.append((496,736))
        #self.mapimages = []
        #self.mapimages.append(pygame.image.load(''))
        
        
        
        self.level = [
        "CCCCCCBBBBBBBBBBBBBBBBBBBBBBBBBC",
        "CCCCBB     BB          BBBA   BC",
        "CCCB                    A     BC",
        "CCCB                          BC",
        "CCB                           BC",
        "CB           AA               BC",
        "CBBCCDCCBBBBBBBBBBBAAAAA      BC",
        "CCCCCDCCCCBBBBB               BC",
        "CCCCCDCCCBB                   BC",
        "CCBBBDBBBB                  BBBC",
        "CCB                           BC",
        "CB                            BC",
        "CB       @    G    @          BC",
        "CB        ABBBBBBBA           BC",
        "CB                           BBC",
        "CCBB                          CC",
        "CC                             C",
        "C                              C",
        "C                             BC",
        "C                 @   G     ABBC",
        "C                  AAABBBBBBBBCC",
        "CBB                         ABCC",
        "CB               T            BC",
        "B     @  G    @                C",
        "B      CCBBBBB                 C",
        "B  T           L               C",
        "B                              C",
        "B                              C",
        "B                              C",
        "CBBBWWWWWWWB                   C",
        "BBBBBAAAAAAAAAAAAAAAAAAAAAAA   C",
        "CCCBBBBBBBBBBBBBBBBBBBBBBAA    C",
        "CCCCCCCCCCCCCCCCCBBBBBBBBA     C",
        "CCCCCCCCCCCCCCCCCCCBBBBBBA     C",
        "CCCCBBBBBBBBBBB                C",
        "CCCCC RBBBB                    C",
        "CBBBB BBAA                  ABBC",
        "CBB                            C",
        "CB                             C",
        "CB       @    G    @  L        C",
        "CB        BBBBBBAAA            C",
        "CB                           ABC",
        "CBBB                          BC",
        "CB                            BC",
        "CB                            BC",
        "CB                            BC",
        "CB                @         BBBC",
        "CB                 AAAABBBBCCCCC",
        "CBBB                        ABBB",
        "CB                              ",
        "CB    @  G    @                 ",
        "CB     CCCCAAA                  ",
        "CB                              ",
        "CBBBBBBABBAAAAAAAAAAAAAAAAAAAAAA",
        "CCCBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"    
        ]
        self.underlaymat = [
        "CCCCCCBBBBBBBBBBBBBBBBBBBBBBBBBC",
        "CCCCBB     BB          BBBA   BC",
        "CCCB                    A     BC",
        "CCCB                          BC",
        "CCB                           BC",
        "CB           AA               BC",
        "CBBCCDCCBBBBBBBBBBBAAAAA      BC",
        "CCCCCDCCCCBBBBB               BC",
        "CCCCCDCCCBB                   BC",
        "CCBBBDBBBB                  BBBC",
        "CCB                           BC",
        "CB                            BC",
        "CB       @    G    @          BC",
        "CB        ABBBBBBBA           BC",
        "CB                           BBC",
        "CCBB                          CC",
        "CC                             C",
        "C                              C",
        "C                             BC",
        "C                 @   G     ABBC",
        "C                  AAABBBBBBBBCC",
        "CBB                         ABCC",
        "CB               T            BC",
        "B     @  G    @                C",
        "B      CCBBBBB                 C",
        "B  T           L               C",
        "B                              C",
        "B                              C",
        "B                              C",
        "CBBBWWWWWWWB                   C",
        "BBBBBAAAAAAAAAAAAAAAAAAAAAAA   C",
        "CCCBBBBBBBBBBBBBBBBBBBBBBAA    C",
        "CCCCCCCCCCCCCCCCCBBBBBBBBA     C",
        "CCCCCCCCCCCCCCCCCCCBBBBBBA     C",
        "CCCCBBBBBBBBBBB                C",
        "CCCCC RBBBB                    C",
        "CBBBB BBAA                  ABBC",
        "CBB                            C",
        "CB                             C",
        "CB       @    G    @  L        C",
        "CB        BBBBBBAAA            C",
        "CB                           ABC",
        "CBBB                          BC",
        "CB                            BC",
        "CB                            BC",
        "CB                            BC",
        "CB                @         BBBC",
        "CB                 AAAABBBBCCCCC",
        "CBBB                        ABBB",
        "CB                            AB",
        "CB    @  G    @                 ",
        "CB     CCCCAAA                  ",
        "CB                              ",
        "CBBBBBBABBAAAAAAAAAAAAAAAAAAAAAA",
        "CCCBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        ]
        self.overlaymat = [
        "CCCCCCBBBBBBBBBBBBBBBBBBBBBBBBBC",
        "CCCCBB     BB          BBBA   BC",
        "CCCB                    A     BC",
        "CCCB                          BC",
        "CCB                           BC",
        "CB           LR               BC",
        "CB  LPPPPPPPRBBLPPPPPPR       BC",
        "CCCCCDCCCCBBBBB               BC",
        "CCCCCDCCCBB                   BC",
        "CCBBBDBBBB                  BPBC",
        "CCB                           BC",
        "CB                            BC",
        "CB       @    G    @          BC",
        "CB        LPPPPPPPR           BC",
        "CB                           BBC",
        "CCBB                          CC",
        "CC                             C",
        "C                              C",
        "C                             BC",
        "C                 @   G     ABBC",
        "C                  LPPPPS PR BCC",
        "CBB                         ABCC",
        "CB               T            BC",
        "B     @  G    @                C",
        "B      LPPPPPR                 C",
        "B  T                           C",
        "B                              C",
        "B                              C",
        "B                              C",
        "CBBBWWWWWWWB                   C",
        "BBBBBAAAAAAALPPPPPPPPPPPPPPR   C",
        "CCCBBBBBBBBBBBBBBBBBBBBBBAA    C",
        "CCCCCCCCCCCCCCCCCBBBBBBBBA     C",
        "CCCCCCCCCCCCCCCCCCCBBBBBBA     C",
        "CCCCBBBBBBBBBBB                C",
        "CCCCCCBBBBB                    C",
        "CBBBB BBAA                  ABBC",
        "CBB                            C",
        "CB                             C",
        "CB       @    G    @           C",
        "CB        LPPPPPPPR            C",
        "CB                           ABC",
        "CBBB                          BC",
        "CB                            BC",
        "CB                            BC",
        "CB                            BC",
        "CB                @         BBBC",
        "CB                 AAAABBBBCCCCC",
        "CBBB                        ABBB",
        "CB                            AB",
        "CB    @  G    @                 ",
        "CB     CCCCAAA                  ",
        "CB                              ",
        "CBBBBBBABBAAAAAAAAAAAAAAAAAAAAAA",
        "CCCBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"    
        ]
            
        
        self.level_build()
        self.layer2_build()
        self.layer0_build()
        self.doors = []
        #self.doors.append()
        door = TeleBlock(496,800,564,816,True)
        self.platforms.append(door)
        #self.doors.append(door)
        self.entities.add(door)
        


# In[557]:

class Level_05(Level):
    

    def __init__(self, player, mapx, mapy):
        
        super().__init__(player)
        self.bg = Surface((TILE_SIZE,TILE_SIZE))
        self.bg.convert()
        self.bg.fill(Color("#000000"))
        self.mapx = mapx
        self.mapy = mapy
        self.name = 'level01'
        
        #self.mapimages.append(pygame.image.load(''))
        
        
        
        self.level = [
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        "C               D                          C",
        "C               D                          C",
        "C               D               @          C",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCB           C",
        "C                              CB          C",
        "C                               CC         C",
        "C   @         @                            C",
        "C    CCCCCCCCC                            BC",
        "C            C            @              BBC",
        "C            C             CCCCCCCCCCCCCCCCC",
        "C            C            CC               C",
        "C        @  BC           CC                C",
        "C         CCCCCC        CC                 C",
        "C                      CC                  C",
        "C                   CCCCCCCC               C",
        "CCBBAAA                                    C",
        "CCCCBBAAAWWWWWWWB                        ABB",
        "CCCCCCCBWWWWWWWWB                      AABBB",
        "CCCCCCCCBBBBBBBBBBBBAAAAAAAAA      AAAABBBBB",
        "PP                                        CC",
        "P                                          C",
        "P                                          C",
        "P                  PPPPPPPPPPPP            C",
        "P                                          C",
        "P       T        T           T       T     C",
        "P                                           ",
        "P                                           ",
        "P  B                                        ",
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]
    
        self.level_build()
        
        


# In[558]:

class Level_02(Level):
    

    def __init__(self, player):
        
        super().__init__(player)
        self.bg = Surface((TILE_SIZE,TILE_SIZE))
        self.bg.convert()
        self.bg.fill(Color("#000000"))
        self.x = 1
        self.y = 2
        self.name = 'level02'
        self.mapcoordinates = []
        self.mapcoordinates.append((1,2))
        self.mapcoordinates.append((2,2))
        self.mapcoordinates.append((1,3))
        self.mapcoordinates.append((2,3))
        #self.entrypoints.append((16,224))
        #self.entrypoints.append((1008,544))
        """
        self.level = [
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "P                              P",
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
        ]
        """
        self.level = [
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "                                                               C",
        "                                                               C",
        "                                                               C",
        "                                                               C",
        "AAAAAAAAAAAAAAA                                                C",
        "CBBBBBBBB                                        CCCCCCCCCCCCCCC",
        "CB                                                             C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                                                              C",
        "C                              CC                              C",
        "C                              CC                              C",
        "C                              CC                              C",
        "C                              CC                              C",
        "C                              CC                               ",
        "C                              CC                               ",
        "C                              CC                               ",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        ]
    
        self.level_build()
        
        #self.doors = []
        #self.doors.append()
        door = TeleBlock(1008,512,1574,1104, True)
        self.platforms.append(door)
        #self.doors.append(door)
        self.entities.add(door)
        
        #self.doors.append()
        door2 = TeleBlock(0,224,440,816, False)
        self.platforms.append(door2)
        #self.doors.append(door)
        self.entities.add(door2)


# In[559]:

class Level_03(Level):
    

    def __init__(self, player):
        
        super().__init__(player)
        self.bg = Surface((TILE_SIZE,TILE_SIZE))
        self.bg.convert()
        self.bg.fill(Color("#000000"))
        self.x = 3
        self.y = 3
        self.name = 'level03'
        self.mapcoordinates = []
        self.mapcoordinates.append((3,3))
        self.mapcoordinates.append((3,4))
        #self.entrypoints.append(())
        
        
        
        self.level = [
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        "C                              C",
        "C                              C",
        "C                              C",
        "C                              C",
        "C     AA                       C",
        "C  A AA                        C",
        "C BBBB                         C",
        "CBBBCC                         C",
        "CBCC                        B  C",
        "CBBBCBBB      BBBB   BBB    B  C",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCC  C",
        "CBBBBBBBBBB                    C",
        "C                              C",
        "                               C",
        "                               C",
        "        G  @                  AC",
        "AAAAAAAAAA                   AAC",
        "BBBBBBBBBBB                 ABBB",
        "CCCCB                      CCBBC",
        "CA                           CCC",
        "C                              C",
        "C                              C",
        "C                              C",
        "C                              C",
        "CB                             C",
        "CB                             C",
        "CBA                  T         C",
        "CBBAAAAAAAAAAA                 C",
        "CBBBBBBBBBB                    C",
        "CBCC                           C",
        "CB                             C",
        "CB                              ",
        "CBB                             ",
        "CBBBBBBBA                       ",
        "CCCCCCCBBBAAAAAAAAAAAAAAAAAAAAAA",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        ]
    
        self.level_build()
        
        
        door = TeleBlock(496,512,2140,1392, True)
        self.platforms.append(door)
        #self.doors.append(door)
        self.entities.add(door)
        
        door2 = TeleBlock(0,224,1480,1104, False)
        self.platforms.append(door2)
        #self.doors.append(door)
        self.entities.add(door2)


# In[560]:

class Level_04(Level):
    

    def __init__(self, player):
        
        super().__init__(player)
        self.bg = Surface((TILE_SIZE,TILE_SIZE))
        self.bg.convert()
        self.bg.fill(Color("#000000"))
        self.x = 4
        self.y = 4
        self.name = 'level04'
        self.mapcoordinates=[]
        self.mapcoordinates.append((4,4))
        
        
        self.level=[
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        "CCCCCCBBBBBBBBBBBBBBBBBBBBBCCCCC",
        "CCBBBBBBBBBBBBBBBBBBBBBBBBBBBBCC",
        "CBBBBBBAAAAA           AAABBBBBC",
        "CBBBB                      ABBBC",
        "CBBBB                        ABC",
        "CBB            T             ABC",
        "CB                           ABC",
        "CB                           ABC",
        "CCDDD        L   T           ABC",
        "CCDDDD                       ABC",
        "CCDDZDD                      ABC",
        "CCCCBCCC                     ABC",
        "BABBAAAB                     ABC", 
        "                             ABC", 
        "                            ABBC",
        "                      G    ABBCC",
        "AAAAAAAAAAAAAAAAAAABBBBAAABBBCCC",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCC",
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        ]
    
        self.level_build()
        door = TeleBlock(0,224,1960,1392, True)
        self.platforms.append(door)
        #self.doors.append(door)
        self.entities.add(door)


# In[561]:

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.image = pygame.image.load("char-10.png")
        self.rect = self.image.get_rect()
        #self.image = Surface((16,16))
        #self.image.fill(RED)
        self.image.convert()
        self.rect = Rect(x, y, 32, 48)
        self.ammo = 100
        self.health = 100
        self.playerface = 1
        self.gravity = 0.7
        self.knockflag = 0
        self.dmgBoost = 0
        self.boostcounter = 0
        self.counter = 0
        self.currentweapon = 0
        self.images = [[0 for i in range(2)] for j in range(10)]
        self.flipcolorflag = False
        altimage = Surface((TILE_SIZE,TILE_SIZE))
        altimage.fill(GREEN)
        altimage.convert()
        #self.images.append(self.image)
        #self.images.append(altimage)
        self.heldfire = False
        self.weaponratecounter = 0
        self.weaponratecounter2 = 0
        self.dmg = 10
        self.stretch = 0
        self.aimx = 0
        self.aimy = 0
        self.load_images()
        self.aimposition =0
        self.jumpheight = 10
        self.jumpcounter = self.jumpheight
        self.candoublejump= False
        self.weaponlist = '1000'
        self.healthcap = 1
        self.ammocap = 100
        self.counter2 = 0
        self.counter3 = 0
        self.speed = 7
        self.jumpspeed = 9
        
        
    def load_images(self):
        for x in range(5):
            for y in range(2):
                imagestring = ('char-%s%s.png' % (x,y) )
                image = pygame.image.load(imagestring)
                image2 = pygame.transform.flip(image, True, False)
                image.convert()
                image2.convert()
                self.images[(2*x)][y] = image
                self.images[((2*x)+1)][y] = image2
            
            
    def hit(self, ent):
        if (self.health >= ent.dmg) and (self.dmgBoost == 0):
            self.health = self.health - ent.dmg
            
            self.flipcolor()
            self.dmgBoost += 1
            
            if self.health == 0:
                self.death()
        elif (self.health < ent.dmg):
            self.death()
        else:
            pass
    def death(self):
        #respawn player at some point in level
        self.health = 100
        self.ammo = 100
        self.rect.x = 64
        self.rect.y =64
    def fire_sustained(self, level):
        #self.weaponratecounter = self.weaponratecounter+1 # weaponratecounter will store number of times 
        #that fire function is called during keydown. reset after keyup
        if self.currentweapon == 0:
            if self.weaponratecounter == 0 or (self.weaponratecounter % 10) == 0: 
                self.fire_bullet(level)
        if self.currentweapon == 1:
            if self.weaponratecounter == 0 or (self.weaponratecounter % 20) == 0: 
                print(self.weaponratecounter)
                self.fire_laser(level)    
        if self.currentweapon == 2:
            if self.weaponratecounter > 0:
                self.stretch.expandcounter += 10
            if self.weaponratecounter == 0: 
                
                self.fire_stretchlaser(level)
        if self.currentweapon == 3:
            if self.weaponratecounter == 0 or (self.weaponratecounter % 100) == 0:
                self.fire_missile(level)
        
      
        self.weaponratecounter = self.weaponratecounter+1


    def fire_bullet(self, level):
        if self.ammo > 0:
            self.ammo -= 1
            
            blt = Bullet(level)
            pygame.mixer.Sound.play(level.soundlist[0])
            
           
            if self.aimposition == 0:
                blt.rect.midbottom = self.rect.midtop

            if self.aimposition == 45:
                blt.rect.midleft = self.rect.topright
            if self.aimposition == 90:
                blt.rect.midleft = self.rect.midright
            if self.aimposition == 135:
                blt.rect.midleft = self.rect.bottomright
            if self.aimposition == 180:
                blt.rect.midtop = self.rect.midbottom
            if self.aimposition == 225:
                blt.rect.midright = self.rect.bottomleft
                #self.image = self.images[5]
            if self.aimposition ==  270:
                blt.rect.midright = self.rect.midleft
            if self.aimposition == 315:
                blt.rect.midright = self.rect.topleft
            level.projectiles.add(blt)
    def fire_missile(self, level):
        if self.ammo > 0:
            self.ammo -= 1
            
            mis = Missile(level)
            if self.aimposition == 0:
                mis.rect.midleft = self.rect.midright

            if self.aimposition == 45:
                mis.rect.midleft = self.rect.topright
            if self.aimposition == 90:
                mis.rect.midbottom = self.rect.midtop
            if self.aimposition == 135:
                mis.rect.midright = self.rect.topright
            if self.aimposition == 180:
                mis.rect.midright = self.rect.midleft
            if self.aimposition == 225:
                mis.rect.midright = self.rect.bottomleft
                #self.image = self.images[5]
            if self.aimposition ==  270:
                mis.rect.midtop = self.rect.midbottom
            if self.aimposition == 315:
                mis.rect.midright = self.rect.topleft
            level.projectiles.add(mis)
    def fire_laser(self, level):
        if self.ammo > 1:
            self.ammo -=2
            las = Laser(level)   
            level.projectiles.add(las)
            if self.aimposition == 0:
                las.rect.midleft = self.rect.midright

            if self.aimposition == 45:
                las.rect.midleft = self.rect.topright
            if self.aimposition == 90:
                las.rect.midbottom = self.rect.midtop
            if self.aimposition == 135:
                las.rect.midright = self.rect.topright
            if self.aimposition == 180:
                las.rect.midright = self.rect.midleft
            if self.aimposition == 225:
                las.rect.midright = self.rect.bottomleft
                #self.image = self.images[5]
            if self.aimposition ==  270:
                las.rect.midtop = self.rect.midbottom
            if self.aimposition == 315:
                las.rect.midright = self.rect.topleft
            level.projectiles.add(las)
    def fire_stretchlaser(self,level):
        if self.ammo >3:
            self.ammo -=4
            self.stretch = StretchLaser(level)
            level.projectiles.add(self.stretch)
            
        
    def flipcolor(self):
        print('hit')
        #if self.flipcolorflag == False:
        #    self.image = self.images[1]
        #    self.flipcolorflag = True
        #else:
        #    self.image = self.images[0]
        #    self.flipcolorflag = False
    def change_weapon(self):
        if self.currentweapon == 0:
            self.currentweapon = 1
            self.dmg = 12
        elif self.currentweapon ==1:
            self.currentweapon = 2
            self.dmg = 20
        elif self.currentweapon == 2:
            self.currentweapon = 3
            self.dmg = 100
        elif self.currentweapon == 3:
            self.currentweapon = 0
            self.dmg = 15
        else:
            pass
    def update(self, aim, jump, up, down, left, right, running, gamemap):
        level = gamemap.level
        
        if (self.heldfire == True):
            self.fire_sustained(level)
            
        else:
            level.soundlist[0].stop()
            self.weaponratecounter = 0
            level.projectiles.remove(self.stretch)
            self.stretch = 0
        if(self.dmgBoost > 0):
            self.dmgBoost += 1
            if self.dmgBoost >= 60:
                self.dmgBoost = 0
                self.flipcolor()
        self.jumpcounter -=1
        if self.counter3 % 8 ==0:
            
            self.counter2 += 1
        
        imagemod = self.counter2 % 2
        if self.knockflag == 0: ##only allow user input if not in knocked back state    
            if jump: ## if jump flag is up aka keyboard button is being held
                if self.onGround:
                    
                    self.yvel = -9
                    self.jumpcounter = self.jumpheight
                    self.onGround = False
                else:
                    if self.jumpheight >= self.jumpcounter > 0:
                        self.yvel = -9
                        
                        
                        
            if not aim:
                if up and right:
                    self.aimposition = 45
                    self.xvel = 7
                    self.image = self.images[2][imagemod]
                    self.counter3 +=1
                elif up and left:
                    self.aimposition = 315
                    self.xvel = -7
                    self.image = self.images[3][imagemod]
                    self.counter3 +=1
                elif down and right:
                    self.aimposition = 135
                    self.xvel = 5
                    self.image = self.images[6][imagemod]
                    self.counter3 +=1
                elif down and left:
                    self.aimposition = 225
                    self.xvel = -5
                    self.image = self.images[7][imagemod]
                    self.counter3 +=1
                elif up:
                    self.aimposition = 0
                    self.image = self.images[0][imagemod]
                elif down:
                    #self.aimposition = 180
                    #self.image = self.images[8][imagemod]
                    pass
                elif left:
                    self.aimposition = 270
                    self.xvel = -7
                    self.image = self.images[5][imagemod]
                    self.counter3 +=1
                elif right:
                    self.aimposition = 90
                    self.xvel = 7
                    self.image = self.images[4][imagemod]
                    self.counter3 +=1
                else:
                    if self.aimposition == 90:
                        self.image = self.images[4][imagemod]
                    elif self.aimposition == 180 or self.aimposition == 135:
                        self.image = self.images[0][imagemod]
                    elif self.aimposition == 0 or self.aimposition == 45:
                        self.aimposition = 90
                        self.image = self.images[0][imagemod]
                    elif self.aimposition == 315 or self.aimposition == 270 or self.aimposition == 225:
                    
                        self.image = self.images[5][imagemod]
                    else:
                        pass
                
            else:
                #aim position defined from origin -> top
                if up and right:
                    self.aimposition = 45
                    self.image = self.images[2][imagemod]
                elif up and left:
                    self.aimposition = 315
                    self.image = self.images[3][imagemod]
                elif down and right:
                    self.aimposition = 135
                    self.image = self.images[6][imagemod]
                elif down and left:
                    self.aimposition = 225
                    self.image = self.images[7][imagemod]
                elif up:
                    self.aimposition = 0
                    self.image = self.images[0][imagemod]
                elif down:
                    self.aimposition = 180
                    self.image = self.images[8][imagemod]
                elif left:
                    self.aimposition = 270
                    self.image = self.images[5][imagemod]
                elif right:
                    self.aimposition = 90
                    self.image = self.images[4][imagemod]
                else:
                    pass
                
                

            
        else: 
            self.counter += 1
            if self.counter == 40:
                self.knockflag = 0
                self.counter = 0
        if not(left or right): 
                self.xvel = self.xvel* 0.88
                if self.xvel < 0.:
                    self.xvel = 0    
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += self.gravity
            # max falling speed
            if self.yvel > 100: self.yvel = 100

        #blt.update()
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, level, gamemap)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False;
        
        # do y-axis collisions
        self.collide(0, self.yvel, level, gamemap)
        if self.yvel == 0 and self.xvel == 0 and self.knockflag >= 20: ##if no velocity after movement + collision
            #player is kicked out of the knocked state
            self.knockflag = 0
        #velocity clamp
        if self.xvel > 20:
            self.xvel =20
        if self.yvel > 40:
            self.xvel=40
        gamemap.level = level
    def collide(self, xvel, yvel, level, gamemap):
        #if not level.boundingbox.contains(self.rect):
            #self.rect.center = [180,96]
        for ent in level.entities:
            if pygame.sprite.collide_rect(self, ent):
                if isinstance(ent, Enemy):
                    self.hit(ent)
                    if xvel > 0: #moving right
                        
                        #self.xvel = 0
                        
                        self.rect.right = ent.rect.left
                        self.xvel = ent.xvel - ent.knockback[0]
                        self.knockflag = 1

                    if xvel < 0: #moving left
                        
                        #self.xvel = 0
                        
                        self.rect.left = ent.rect.right
                        self.xvel = ent.xvel + ent.knockback[0]
                        self.knockflag = 1
                       
                    if yvel>0: #moving down
                        
                        ent.yvel = 0
                        #self.xvel = 0
                        
                        self.rect.bottom = ent.rect.top
                        
                        self.onGround = True
                        
                        
                        
                        #jump = False
                        ent.underPlayer = True
                        self.yvel = -self.yvel*0.3 -ent.knockback[1]
                        if self.rect.centerx > ent.rect.centerx:
                            self.xvel = ent.knockback[0]
                        else:
                            self.xvel = -ent.knockback[0]
                            #self.xvel = -self.xvel*0.2 - ent.knockback[0]
                        self.knockflag = 1
                    if yvel<0: #moving up
                        self.rect.top = ent.rect.bottom
                        
                        self.knockflag = 1
                        
                        if self.rect.centerx > ent.rect.centerx:
                            self.xvel += ent.knockback[1]
                        else:
                            self.xvel -= ent.knockback[1]
                            
                       # self.yvel += ent.knockback[1]
                    if yvel == 0 and xvel ==0: ##standstill - enemy collided with us
                        if ent.xvel >0: # enemy approaches from left, right collision
                            #self.rect.left = ent.rect.right
                            self.xvel = ent.xvel + ent.knockback[1]
                            
                        if ent.xvel <0: #enemy approaches from right, left collision
                            #self.rect.right = ent.rect.left
                            self.xvel = ent.xvel-ent.knockback[1]
                            
                        if ent.yvel>0: #enemy approaches from top
                            self.rect.top = ent.rect.bottom
                            #ent.rect.bottom = self.rect.top
                            if self.rect.centerx > ent.rect.centerx:
                                self.xvel += ent.knockback[1]
                            else:
                                self.xvel -= ent.knockback[1]

        for p in level.platforms:
                            
                #true when touching, false when not
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, TeleBlock):
                    level.teleX = p.x2
                    level.teleY = p.y2
                    
                    
                    

                if isinstance(p, StoneFace):
                    p.colflag = True
                
                    
                if xvel > 0:
                    self.rect.right = p.rect.left
                    
                if xvel < 0:
                    self.rect.left = p.rect.right
                    
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                    self.jumpcounter = 20
                    
                    #self.knockflag = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
                if isinstance(p, SpikeBlock):
                    self.yvel = -10
                    self.hit(p)


# In[562]:

class Enemy(Entity):
    def __init__(self, level, x, y):
        super().__init__()
        self.xvel = 0
        self.yvel = 0
        self.level = level
        self.player = level.player
        self.image = Surface((32,32))
        self.image.fill(RED)
        self.rect = Rect(x,y,32,32)
        self.level.entities.add(self)
    def inRange(self):
        Xdist = abs(self.player.rect.x - self.rect.x)
        Ydist = abs(self.player.rect.y- self.rect.y)
        playerRange = m.sqrt((Xdist**2)+(Ydist**2))
        return playerRange


# In[563]:

class Goop(Enemy):
    def __init__(self, level, x, y):
        super().__init__(level, x, y)

        self.onGround = False
        self.health = 30
        self.playerface = 1
        self.gravity = 0.7
        self.counter = 0
        self.timestep = 1
        self.knockback = [6,6]
        self.level = level
        self.directionflag = True
        self.motionflag = False
        #self.xvel = 0
        self.dmg = 5
        self.ind = 0
        self.images = []
        self.images.append(pygame.image.load('goop2.png').convert_alpha())
        self.images.append(pygame.image.load('goop3.png').convert_alpha())
        self.images.append(pygame.image.load('goop4.png').convert_alpha())
        self.images.append(pygame.image.load('goop1.png').convert_alpha())
        self.image = self.images[0]
        self.revimages = []
        self.revimages.append(pygame.transform.flip(self.images[0], True, False))
        self.revimages.append(pygame.transform.flip(self.images[1], True, False))
        self.revimages.append(pygame.transform.flip(self.images[2], True, False))
        self.revimages.append(pygame.transform.flip(self.images[3], True, False))
        
    
    def hit(self):
        self.health = self.health - self.player.dmg
        if self.health <= 0:
            self.level.entities.remove(self)
    def update(self):
        self.counter = self.counter+1
        modulo180 = self.counter % 180
        modulo120 = self.counter % 100
        
        
        if (self.counter % 40) == 0:
            self.ind +=1
            if self.directionflag == True:
                self.image = self.revimages[self.ind]
            else:
                self.image = self.images[self.ind]
            if self.ind == 3:
                self.ind =0
        if self.counter == 40:
            if self.directionflag == True:
                self.xvel += 1
            else:
                self.xvel -= 1
            
        if self.counter == 120:
            self.xvel = 0
            self.counter = 0
            
        
        
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += self.gravity
            # max falling speed
            if self.yvel > 100: self.yvel = 100
      #  if not(left or right):
        #    self.xvel = 0
        #self.edgecheck()
        #blt.update()
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        self.underPlayer = False
        # do y-axis collisions
        self.collide(0, self.yvel)
 #enemy class has to check for collisions with platforms, player, and projectiles
    def collide(self, xvel, yvel):
        for p in self.level.platforms:
            if pygame.sprite.collide_rect(self, p):
                
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.xvel = -self.xvel
                    self.directionflag = False
                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.xvel = -self.xvel
                    self.directionflag = True
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
        
        for p in self.level.invisiblocks:
            if pygame.sprite.collide_rect(self, p):
            
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.xvel = -self.xvel
                    self.directionflag = False
                
                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.xvel = -self.xvel
                    self.directionflag = True
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
               


# In[564]:

class Runner(Enemy):
    def __init__(self, level, x, y):
        super().__init__(self, level, x, y)

        self.onGround = False

    
        self.health = 100
        self.playerface = 1
        self.gravity = 0.7
        self.counter = 0
        self.timestep = 1
        self.knockback = [20,6]
        self.level = level
        self.underPlayer = False
        self.directionflag = False
        self.xvel = 7
        self.dmg = 7
    def hit(self):
        self.health = self.health - self.player.dmg
        if self.health <= 0:
            self.level.entities.remove(self)
    def update(self):
        self.counter = self.counter+1
        modulo180 = self.counter % 180
        modulo120 = self.counter % 100
        #if self.directionflag == True:
        #    self.xvel = -self.xvel
        #    self.directionflag = False
        if (modulo120 == 0):
            self.counter = 0
            self.yvel = -18
            self.onGround = False
            
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += self.gravity
            # max falling speed
            if self.yvel > 100: self.yvel = 100
      #  if not(left or right):
        #    self.xvel = 0

        #blt.update()
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        self.underPlayer = False
        # do y-axis collisions
        self.collide(0, self.yvel)
 #enemy class has to check for collisions with platforms, player, and projectiles
    def collide(self, xvel, yvel):
        for p in self.level.platforms:
            if pygame.sprite.collide_rect(self, p):
                #if isinstance(p, ExitBlock):
                #    pygame.event.post(pygame.event.Event(QUIT))
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.xvel = -self.xvel
                   # directionFlag = True
                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.xvel = -self.xvel
                   # directionFlag = True
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
               # if yvel == 0:
       # for ent in self.level.entities:
            #if pygame.sprite.collide_rect(self, ent):
                #if isinstance(ent, Player):
                    #if yvel>0:
                      #  self.rect.bottom = ent.rect.top
                       # self.onGround = True
                      #  self.yvel = 0
                    #if yvel<0:
                        #ent.rect.bottom = self.rect.top


# In[565]:

class Pickup(Entity):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.player = self.level.player
        self.level.pickups.add(self)


# In[566]:

class DoubleJump(Pickup):
    def __init__(self, level, xpos, ypos):
        super().__init__(level)
        self.image = pygame.image.load("doublejump-1.png")
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
    def update(self, dial):
        block_hit_list = pygame.sprite.spritecollide(self, self.level.entities, False)
        if block_hit_list:
            self.level.player.jumpheight = 16
            dial.dString = "    Jump Height Increased"
            self.level.pickups.remove(self)
        


# In[567]:

class AmmoPickup(Pickup):
    def __init__(self, level, xpos, ypos):
        super().__init__(level)

        width = 8
        height = 8
        #self.image = pygame.image.load("spritey.png")
        
        self.image = pygame.Surface([width, height])
        self.image.fill(GOLD)
 
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        # Set speed vector of pickup
        self.change_x = 0
        self.change_y = 0

        

    def update(self, dial):
        
        block_hit_list = pygame.sprite.spritecollide(self, self.level.entities, False)
        if block_hit_list:
            print('pickup')
            self.level.player.ammo += 10
            self.level.pickups.remove(self)


# In[568]:

class HealthPickup(Pickup):
    def __init__(self, level, xpos, ypos):
        super().__init__(level)

        width = 8
        height = 8
        self.image = pygame.image.load("powerup1-1.png")
        self.image.convert_alpha()
        
        #self.image = pygame.Surface([width, height])
        #self.image.fill(GOLD)
 
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        # Set speed vector of pickup
        self.change_x = 0
        self.change_y = 0
        self.h =self.level.player.health
        

    def update(self,dial):
        
        block_hit_list = pygame.sprite.spritecollide(self, self.level.entities, False)
        if block_hit_list:
            h = self.level.player.health
            
            if h < 91:
                h += 10
            elif h > 90 and h < 101:
                h =100
            else:
                pass
            self.level.player.health = h
            self.level.pickups.remove(self)
   


# In[569]:

class Proj(Entity):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.level.projectiles.add(self)
        self.aimposition = self.level.player.aimposition
        self.xvel =0
        self.yvel =0
        self.revflag = False
    def rotateImage(self, angle):
        self.image=pygame.transform.rotate(self.image,angle)
    def velSetter(self):
        self.shift = 90
        if self.aimposition == 0:
            self.yvel = -1
            
        elif self.aimposition ==45:
            self.xvel = 1/1.44
            self.yvel = -1/1.44
        elif self.aimposition == 90:
            self.xvel = 1
        elif self.aimposition == 135:
            self.yvel = 1/1.44
            self.xvel = 1/1.44
        elif self.aimposition == 180:
            self.yvel = 1/1.44
        elif self.aimposition == 225:
            self.revflag = True
            self.xvel = -1/1.44
            self.yvel = 1/1.44
        elif self.aimposition == 270:
            self.revflag = True
            self.xvel = -1
        elif self.aimposition == 315:
            self.revflag = True
            self.yvel = -1/1.44
            self.xvel = -1/1.44    
        else:
            self.yvel = -1
        rotate = self.aimposition +self.shift
        self.rotateImage(rotate)
        


# In[570]:

class Missile(Proj):
    def __init__(self, level):
        super().__init__(level)

        width = 7
        height = 4
        bulletspeed = 5
        self.revflag = False
        #self.image = pygame.image.load("spritey.png")
        
        self.image = pygame.image.load('missile-1.png').convert_alpha()
        self.images = []
        self.images.append(self.image)
        self.images.append(pygame.image.load('missile-2.png').convert_alpha())
        self.images.append(pygame.image.load('missile-3.png').convert_alpha())

        self.revimages = []
        self.revimages.append(pygame.transform.flip(self.images[0], True, False))
        self.revimages.append(pygame.transform.flip(self.images[1], True, False))
        self.revimages.append(pygame.transform.flip(self.images[2], True, False))

        self.ind= 0
        self.counter = 0
        self.basefiringrate = 10
        self.rect = self.image.get_rect()
 
        self.velSetter()
        self.xvel = self.xvel*bulletspeed
        self.yvel = self.yvel*bulletspeed

            
        if self.revflag == False:
                self.image = self.images[self.ind]
        else:
                self.image = self.revimages[self.ind]
        
    def update(self):
        self.counter +=1
        if self.counter % 6 == 0:
            self.ind +=1
            if self.revflag == False:
                self.image = self.images[self.ind]
            else:
                self.image = self.revimages[self.ind]
            if self.xvel>0:
                self.xvel +=1
            else:
                self.xvel -=1
            if self.yvel>0:
                self.yvel +=1
            elif self.yvel<0:
                self.yvel -=1
            else: 
                pass
        
        
        if self.ind >1:
            self.ind = 0
        self.rect.x += self.xvel
        self.rect.y += self.yvel
        for p in self.level.platforms:
            if pygame.sprite.collide_rect(self,p):
                self.level.projectiles.remove(self)
        for ent in self.level.entities:
            if pygame.sprite.collide_rect(self,ent):
                if isinstance(ent, Enemy):
                    ent.hit()
                    self.level.projectiles.remove(self)
                if isinstance(ent, DestBlock):
                    self.level.entities.remove(ent)
                    self.level.platforms.remove(ent)
                    self.level.projectiles.remove(self)


# In[571]:

class Laser(Proj):
    def __init__(self, level):
        super().__init__(level)

        width = 20
        height = 2
        bulletspeed = 30
        #self.image = pygame.image.load("spritey.png")

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()

        self.xvel = bulletspeed
        self.yvel = 0
        
        self.velSetter()
        self.xvel = self.xvel*bulletspeed
        self.yvel = self.yvel*bulletspeed

        #if self.level.player.playerface == 0:
        #   self.xvel = -bulletspeed
    def update(self):

        self.rect.x += self.xvel
        self.rect.y += self.yvel
        for p in self.level.platforms:
            if pygame.sprite.collide_rect(self,p):
                self.level.projectiles.remove(self)
        for ent in self.level.entities:
            if pygame.sprite.collide_rect(self,ent):
                if isinstance(ent, Enemy):
                    ent.hit()
                    self.level.projectiles.remove(self)


# In[572]:

class StretchLaser(Proj):
    def __init__(self, level):
        super().__init__(level)

        #self.width = 7
        #self.height = 4
        self.bulletspeed = 10
        self.origimage = pygame.image.load("laser1.png")
        self.rect = self.origimage.get_rect()
        self.width = self.rect.w
        self.height = self.rect.h
        self.image = pygame.image.load("BLAST1-1.png")
        self.image.convert_alpha()
        self.origimage.convert()
        
        self.basefiringrate = 10
        #self.rect = self.image.get_rect()
        self.expandcounter = 0
        self.imagetrans = 0
 
        if self.level.player.playerface == 0:
            self.rect.midright = self.level.player.rect.midleft
        else:
            self.rect.midleft = self.level.player.rect.midright
    def update(self):
        
        self.expandcounter = self.expandcounter + self.bulletspeed
        
        #self.imagerot = pygame.transform.rotate(self.origimage, self.aimposition) 
        if self.aimposition == 0:
            self.rect.midleft = self.level.player.rect.midright
            #self.image = pygame.transform.smoothscale(self.origimage, (self.width+self.expandcounter, self.height))
            #self.rect = self.image.get_rect()
        if self.aimposition == 45:
            self.rect.midleft = self.level.player.rect.topright
            #self.image = pygame.transform.smoothscale(self.origimage, (self.width+self.expandcounter, self.height)
            #self.rect = self.image.get_rect()
        if self.aimposition == 90:
            self.rect.midbottom = self.level.player.rect.midtop
            #self.image = pygame.transform.smoothscale(self.origimage, (self.width+self.expandcounter, self.height))
            #self.rect = self.image.get_rect()
        if self.aimposition == 135:
            self.rect.midright = self.level.player.rect.topright
            #self.image = pygame.transform.smoothscale(self.imagerot, (self.width+self.expandcounter, self.height +self.expandcounter))
            #self.rect = self.image.get_rect()
        if self.aimposition == 180:
            self.rect.midright = self.level.player.rect.midleft
            #self.image = pygame.transform.smoothscale(self.imagerot,(self.width+self.expandcounter, self.height))
            #self.rect = self.image.get_rect()
        if self.aimposition == 225:
            self.rect.midright = self.level.player.rect.bottomleft
            #self.image = pygame.transform.smoothscale(self.imagerot,(self.width+self.expandcounter, self.height+expandcounter))
        if self.aimposition ==  270:
            self.rect.midtop = self.level.player.rect.midbottom 
        
        self.image = pygame.transform.smoothscale(self.origimage, (self.width+self.expandcounter, self.height))
        #self.image = pygame.transform.rotate(self.imagetrans, self.aimposition)

        for p in self.level.platforms:
            if pygame.sprite.collide_rect(self,p):
                self.level.projectiles.remove(self)
        for ent in self.level.entities:
            if pygame.sprite.collide_rect(self,ent):
                if isinstance(ent, Enemy):
                    ent.hit()
                    self.level.projectiles.remove(self)


# In[573]:

class Bullet(Proj):
    def __init__(self, level):
        super().__init__(level)

        width = 7
        height = 4
        bulletspeed = 15
        #self.image = pygame.image.load("spritey.png")
        
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.basefiringrate = 10
        self.rect = self.image.get_rect()
 
        self.velSetter()
        self.xvel = self.xvel*bulletspeed
        self.yvel = self.yvel*bulletspeed
        #pygame.mixer.music.load('bullet.wav')
        #pygame.mixer.music.play(0)
        
    def update(self):

        self.rect.x += self.xvel
        self.rect.y += self.yvel
        for p in self.level.platforms:
            if pygame.sprite.collide_rect(self,p):
                self.level.projectiles.remove(self)
        for ent in self.level.entities:
            if pygame.sprite.collide_rect(self,ent):
                if isinstance(ent, Enemy):
                    ent.hit()
                    self.level.projectiles.remove(self)


# In[574]:

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load('stonewall-16.png')
        self.image.convert()
        
        
        
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)

    def update(self):
        pass


# In[575]:

class Water(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load('watertile-1.png')
        self.image.convert()
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)

    def update(self):
        pass


# In[576]:

class GroundCover(Entity):
    def __init__(self, x, y, case):
        Entity.__init__(self)
         
        if case is 'center':
            self.image = pygame.image.load('purplegrass-1.png')
        elif case is 'left':
            self.image = pygame.image.load('purplegrass-3.png')
        else:
            self.image = pygame.image.load('purplegrass-2.png')
        self.image.convert()
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)

    def update(self):
        pass


# In[577]:

class GradientPlatform(Entity):
    def __init__(self, x, y, lightlevel):
        Entity.__init__(self)
        if lightlevel == 0:
            self.image = pygame.image.load('bluerock1-1.png')
        elif lightlevel ==1:
            self.image = pygame.image.load('bluerock1-3.png')
        elif lightlevel ==2:
            self.image = pygame.image.load('bluerock1-2.png')
        else:
            self.image = pygame.image.load('bluerock1-1.png')
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)
    def update(self):
        pass


# In[578]:

class SpikeBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.image.load('stonewall-16.png')
        self.image.convert()
        self.dmg = 10


# In[579]:

class StoneFace(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = None
        self.altimage = pygame.image.load('faceblock-1.png')
        self.altimage.convert_alpha()
        self.altimage2 = pygame.image.load('faceblock-2.png')
        self.altimage2.convert_alpha()
        self.colflag = False
        self.imageflag = False
        self.image = self.altimage
    def update(self):
        
        if self.colflag == True:
            self.image = self.altimage2
        else:
            self.image = self.altimage
        
            


# In[580]:

class DestBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.image.load('bluerock1-2.png')
        self.image.convert()


# In[581]:

class Gem(Platform):
    def __init__(self, x, y, orientation):
        Platform.__init__(self, x, y)
        if orientation:
            self.image = pygame.image.load('bigcrystal.png')
            self.image.convert_alpha()
        else:
            self.image = pygame.image.load('bigcrystal2.png')
            self.image.convert_alpha()
        


# In[582]:

class InvisiBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)


# In[583]:

class TeleBlock(Platform):
    def __init__(self, x, y, x2, y2, orientation):
        Platform.__init__(self, x, y)
        if orientation:
            self.image = pygame.image.load('door-1.png')
            self.image.convert()
        else:
            self.image = pygame.image.load('door-2.png')
            self.image.convert()
        self.x2 = x2
        self.y2 = y2
        self.rect = Rect(x, y, TILE_SIZE, 48)


# In[584]:

class MainMenu(object):
    def __init__(self):
        #object is created at beginning of main loop, but not updated or drawn unless in the "menu" state.
        self.menu = pygame.Surface([WIN_WIDTH, WIN_HEIGHT])
        self.menu.fill(BLACK)
        self.rect = self.menu.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.myfont = pygame.font.SysFont("monospace", 15)
        self.counter = 0
        self.ind = 0       
        self.start = False
        self.title = pygame.image.load('Title1-1.png')          
        self.buttonUnpressed = pygame.Surface([100, 25])
        self.buttonUnpressed.fill(LGREEN)
        #self.buttonUnpressed.rect = self.buttonUnpressed.get_rect()
        self.buttonPressed = pygame.Surface([100, 25])
        self.buttonPressed.fill(DARKGR)
        #self.buttonPressed.rect = self.buttonPressed.get_rect()
        self.button = self.buttonUnpressed
    def update(self, mouse, mouseclick):
        self.counter += 1
        if ((HALF_WIDTH-50)<mouse[0]<(HALF_WIDTH+50)) and (340<mouse[1]<365):
            self.button = self.buttonPressed
            if mouseclick:
                self.start = True
                
        else:
            self.button = self.buttonUnpressed
            
            
        
   
    def draw(self, screen):
        
        
        label2 = self.myfont.render(("START"), 1, (0,0,0))
        screen.blit(self.menu,(self.rect.x, self.rect.y))
        screen.blit(self.title, ((HALF_WIDTH-180), (HALF_HEIGHT-90) ))
        screen.blit(self.button, ((HALF_WIDTH-50), (HALF_HEIGHT+50))) 
        screen.blit(label2, ((HALF_WIDTH-25), (HALF_HEIGHT+54)))


# In[585]:

class Dialog(pygame.sprite.Sprite):
    def __init__(self, gameMap):
        #object is created at beginning of main loop, but not updated or drawn unless in the "pause" state.
        super().__init__()
        self.dString = ""
        self.map = gameMap
        self.width = WIN_WIDTH/4
        self.height = WIN_HEIGHT/4
        self.wind = pygame.Surface([self.width, self.height])
        self.wind.fill(GREY)
        self.rect = self.wind.get_rect()
        self.rect.x = WIN_WIDTH/2 -self.width/2
        self.rect.y = WIN_HEIGHT/2 - self.height/2
        self.myfont = pygame.font.SysFont("monospace", 15)
        self.counter = 0
        self.ind = 0       
        self.back = False
                  
        self.buttonUnpressed = pygame.Surface([100, 25])
        self.buttonUnpressed.fill(LGREY)
        #self.buttonUnpressed.rect = self.buttonUnpressed.get_rect()
        self.buttonPressed = pygame.Surface([100, 25])
        self.buttonPressed.fill(DGREY)
        #self.buttonPressed.rect = self.buttonPressed.get_rect()
        self.button = self.buttonUnpressed
    def update(self, mouse, mouseclick):
        #self.dString = dialogString
        self.counter += 1
        if ((self.rect.x + self.width/2 - 50)<mouse[0]<(self.rect.x + self.width/2 + 50)) and ((self.rect.y + self.height/2 +25)<mouse[1]<(self.rect.y + self.height/2 +50)):
            self.button = self.buttonPressed
            if mouseclick:
                self.back = True
                
        else:
            self.button = self.buttonUnpressed
            
            
        
   
    def draw(self, screen):
        
        label = self.myfont.render((self.dString), 1, (255,255,0))
        label2 = self.myfont.render(("Back"), 1, (255,255,0))
        screen.blit(self.wind,(self.rect.x, self.rect.y))
        screen.blit(self.button, ((self.rect.x + self.width/2 - 50), (self.rect.y + self.height/2 +25)))
        screen.blit(label2, ((self.rect.x + self.width/2 - 50), (self.rect.y + self.height/2 + 25)))
        screen.blit(label, (WIN_WIDTH/2 - self.width/2, ((WIN_HEIGHT/2)-50)))


# In[586]:

class PauseMenu(pygame.sprite.Sprite):
    def __init__(self, gameMap):
        #object is created at beginning of main loop, but not updated or drawn unless in the "pause" state.
        super().__init__()
        self.map = gameMap
        self.width = WIN_WIDTH/2
        self.height = WIN_HEIGHT/2
        self.menu = pygame.Surface([self.width, self.height])
        self.menu.fill(GREY)
        self.rect = self.menu.get_rect()
        self.rect.x = WIN_WIDTH/2 -self.width/2
        self.rect.y = WIN_HEIGHT/2 - self.height/2
        self.myfont = pygame.font.SysFont("monospace", 15)
        self.counter = 0
        self.ind = 0       
        self.back = False
                  
        self.buttonUnpressed = pygame.Surface([100, 25])
        self.buttonUnpressed.fill(LGREY)
        #self.buttonUnpressed.rect = self.buttonUnpressed.get_rect()
        self.buttonPressed = pygame.Surface([100, 25])
        self.buttonPressed.fill(DGREY)
        #self.buttonPressed.rect = self.buttonPressed.get_rect()
        self.button = self.buttonUnpressed
    def update(self, mouse, mouseclick):
        self.counter += 1
        if (480<mouse[0]<580) and (324<mouse[1]<349):
            self.button = self.buttonPressed
            if mouseclick:
                self.back = True
                
        else:
            self.button = self.buttonUnpressed
            
            
        
   
    def draw(self, screen):
        
        label = self.myfont.render(("Menu"), 1, (255,255,0))
        label2 = self.myfont.render(("Back"), 1, (255,255,0))
        screen.blit(self.menu,(self.rect.x, self.rect.y))
        screen.blit(self.button, (WIN_WIDTH/2, ((WIN_HEIGHT/2)+50)) )
        screen.blit(label2, (WIN_WIDTH/2, ((WIN_HEIGHT/2)+50)))
        screen.blit(label, (WIN_WIDTH/2, ((WIN_HEIGHT/2)-50)))


# In[587]:

class HUD(pygame.sprite.Sprite):
    def __init__(self, gameMap):
        super().__init__()
        self.level = gameMap.level
        self.player = gameMap.level.player
        self.ammo = 0
        self.health =0
        self.imageload()
        self.map = gameMap
        self.rect.x = 0
        self.rect.y = WIN_HEIGHT - 100
        self.myfont = pygame.font.SysFont("monospace", 15)
        self.counter = 0
        self.ind = 0       
        self.mapinit()
        self.barmaxsize = 200
        #self.level.hud_list.add(self)
        self.update()
    def imageload(self):
        
        self.hud= []
        for x in range(12):
            self.hud.append(pygame.image.load("HUD1-%s.png"%(x+1)).convert_alpha())
        self.rect = self.hud[0].get_rect()
        self.bar = self.hud[0]
        self.weapimages = []
        self.altweapimages = []
        for x in range(4):
            self.weapimages.append(pygame.image.load("weaponicons-%s.png"%(x+1)).convert_alpha())
            self.altweapimages.append(pygame.image.load("weaponicons-%s2.png"%(x+1)).convert_alpha())
            
    def mapinit(self):
        self.unitx = 14
        self.unity = 8
        self.mapleft =WIN_WIDTH - 155
        self.maptop = WIN_HEIGHT -90
        self.mapbox = pygame.Surface([140, 80])
        
        self.mapbox.fill(BLACK)
        self.mapbox.convert()
        self.grid = [[0 for x in range(self.map.w)] for y in range(self.map.h)] 
        for row in range(len(self.map.grid)):
            for col in range(len(self.map.grid[row])):
                if self.map.grid[row][col]:
                    self.grid[row][col] = Surface((13,7))
                   
                    if self.map.currentx == col and self.map.currenty == row:
                        self.grid[row][col].fill(PINK)
                    else:
                        self.grid[row][col].fill(RED)
                    self.grid[row][col].convert()
                    
        
    def update(self):
        self.map.get_player_coordinates()
        self.counter += 1
        self.ammo = self.player.ammo
        self.health = self.player.health
        
        if not (self.counter % 12):
             
            self.bar = self.hud[self.ind]
            self.ind += 1
            if self.ind == 11:
                self.ind = 0
    
        
        for row in range(len(self.map.grid)):
            for col in range(len(self.map.grid[row])):
                if self.map.grid[row][col]:
                    if self.map.mapco[0] == col and self.map.mapco[1] == row:
                        self.grid[row][col].fill(PINK)
                    else:
                        self.grid[row][col].fill(RED)
        #self.mapdraw()
    #def mapupdate(self):
        
    def mapdraw(self, screen):
        #unit = 16

        screen.blit(self.mapbox, (self.mapleft,self.maptop ))
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                if self.grid[row][col] is not 0:
                    screen.blit(self.grid[row][col], (self.mapleft+col*self.unitx, self.maptop + row*self.unity))
    def bardraw(self, screen):
        size = self.barmaxsize*(self.player.health/100)
        if size ==0:
            size = 1
        bar = pygame.Surface([size, 12])
        bar.fill(RED)
        screen.blit(bar, (260,  WIN_HEIGHT - 52))
    def draw(self, screen):
        label = self.myfont.render(("AMMO: %s" % self.player.ammo), 1, DARKGR)
        
        screen.blit(self.bar,(self.rect.x, self.rect.y))
        if self.level.player.currentweapon == 0:
            screen.blit(self.weapimages[0], (10, WIN_HEIGHT - 100))
            screen.blit(self.altweapimages[1], (10, WIN_HEIGHT-78))
            screen.blit(self.altweapimages[2], (10, WIN_HEIGHT- 56))
            screen.blit(self.altweapimages[3], (10, WIN_HEIGHT - 34))
            
        elif self.level.player.currentweapon == 1:
            screen.blit(self.altweapimages[0], (10, WIN_HEIGHT - 100))
            screen.blit(self.weapimages[1], (10, WIN_HEIGHT-78))
            screen.blit(self.altweapimages[2], (10, WIN_HEIGHT- 56))
            screen.blit(self.altweapimages[3], (10, WIN_HEIGHT - 34))
        elif self.level.player.currentweapon == 2:
            screen.blit(self.altweapimages[0], (10, WIN_HEIGHT - 100))
            screen.blit(self.altweapimages[1], (10, WIN_HEIGHT-78))
            screen.blit(self.weapimages[2], (10, WIN_HEIGHT- 56))
            screen.blit(self.altweapimages[3], (10, WIN_HEIGHT - 34))
        elif self.level.player.currentweapon == 3:
            screen.blit(self.altweapimages[0], (10, WIN_HEIGHT - 100))
            screen.blit(self.altweapimages[1], (10, WIN_HEIGHT-78))
            screen.blit(self.altweapimages[2], (10, WIN_HEIGHT- 56))
            screen.blit(self.weapimages[3], (10, WIN_HEIGHT - 34))
        else:
            pass
        self.mapdraw(screen)
        
        screen.blit(label, (260, WIN_HEIGHT-38))
        self.bardraw(screen)


# In[588]:

class SaveLoadState(object):
    def __init__(self):
        self.savestates= []
        self.statedict = {}
    def save(self, gameMap):
        
        
        self.statedict['level_name'] = gameMap.level.name
         
        self.statedict['player_pos'] = gameMap.level.player.rect
        self.statedict['player_h'] = gameMap.level.player.health
        self.statedict['player_a'] = gameMap.level.player.ammo
        self.statedict['player_h_cap'] = gameMap.level.player.healthcap ##add later
        self.statedict['player_a_cap'] = gameMap.level.player.ammocap
        self.statedict['player_weapon_list'] = gameMap.level.player.weaponlist
        
        print(self.statedict)
   # def load(self):


# In[589]:

def main():
    global cameraX, cameraY
    pygame.init()
    
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("DYNAMO")
    clock = pygame.time.Clock()
    player = Player(160, 72)
    #pygame.mixer.music.load('firstlevelworking.wav')
    #pygame.mixer.music.play(-1)
    
    # winheight and winwidth
    winheight = ROOM_SIZE[1] #288
    winwidth = ROOM_SIZE[0] #512
    size =(1024, 576)
    transurf = pygame.Surface((winwidth, winheight))
    
    up = down = left = right = running = fireWeapon = jump = aim = mouseclick = pause = False
    pause = False
    menuflag = True
    mainmenu = MainMenu()
    gameMap = Map(player)
    save = SaveLoadState()
    save.save(gameMap)
    keyholdflag = True

    jumpholdtimer = 0
    dial = Dialog(gameMap)
    camera = Camera(complex_camera, gameMap.level.total_level_width, gameMap.level.total_level_height)
    gameMap.level.entities.add(player)
    #enemy = Enemy(level, 96, 64)
    #level.entities.add(enemy)
    hud = HUD(gameMap)
    pausemenu = PauseMenu(gameMap)
    done = False
    
    while not done:
        
        clock.tick(60)
        if not (gameMap.level.teleX == 0) and not (gameMap.level.teleY == 0):
            gameMap.switch_level(gameMap.level.teleX, gameMap.level.teleY)
            player.rect.x = gameMap.globalcoordinatex - gameMap.level.x*ROOM_SIZE[0]
            player.rect.y = gameMap.globalcoordinatey - gameMap.level.y*ROOM_SIZE[1]
            camera.__init__(complex_camera, gameMap.level.total_level_width, gameMap.level.total_level_height)
            gameMap.level.entities.add(player)
            #gameMap.level.teleX = 0
            #gameMap.level.teleY = 0
            
            print(player.rect)
        
        for e in pygame.event.get():
            if e.type == QUIT: done= True
            if e.type==VIDEORESIZE:
                screen=pygame.display.set_mode(e.dict['size'],HWSURFACE|DOUBLEBUF|RESIZABLE)
                size = e.dict['size']
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                done= True
            if e.type == KEYDOWN and e.key == K_w:
                up = True
            if e.type == KEYDOWN and e.key == K_s:
                down = True
            if e.type == KEYDOWN and e.key == K_SPACE:
                jump = True                
            if e.type == KEYDOWN and e.key == K_a:
                left = True
                player.playerface = 0
            if e.type == KEYDOWN and e.key == K_d:
                right = True
                player.playerface= 1
            if e.type == KEYDOWN and e.key == K_q:
                save.save(gameMap)
            if e.type ==KEYDOWN and e.key == K_n:
                if pause:
                    pause = False
                else:
                    pause = True
            if e.type == KEYDOWN and e.key == K_RSHIFT:
                player.heldfire = True
            if e.type == KEYDOWN and e.key == K_RCTRL:
                aim = True
            if e.type == KEYDOWN and e.key == K_x:
                player.change_weapon()            
            if e.type == KEYDOWN and e.key == K_f:
                gameMap.level.goopSpawn(96,64)
            if e.type == KEYDOWN and e.key == K_p:
                gameMap.level.H_pickupSpawn((player.rect.x+50),(player.rect.y-50))
            if e.type == KEYUP and e.key == K_RSHIFT:
                player.heldfire = False
            if e.type ==KEYUP and e.key == K_SPACE:
                jump = False
            if e.type == KEYUP and e.key == K_RCTRL:
                aim = False
            if e.type == KEYUP and e.key == K_w:
                up = False
            if e.type == KEYUP and e.key == K_s:
                down = False
            if e.type == KEYUP and e.key == K_d:
                right = False
            if e.type == KEYUP and e.key == K_a:
                left = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                mouseclick = True
            if e.type == pygame.MOUSEBUTTONUP:
                mouseclick = False

        mouse = pygame.mouse.get_pos()
        if menuflag:
            mainmenu.update(mouse,mouseclick)
            mainmenu.draw(screen)
            if mainmenu.start:
                menuflag= False
        elif pause and not menuflag:
            pausemenu.update(mouse, mouseclick)
            pausemenu.draw(screen)
            if pausemenu.back:
                pause = False
                pausemenu.back = False
        elif (dial.dString is not "") and not menuflag and not pause:
            dial.update(mouse, mouseclick)
            dial.draw(screen)
            if dial.back:
                dial.dString = ""
            
            
            
        elif not pause and not menuflag:
            for y in range(len(gameMap.level.level)):
                for x in range(len(gameMap.level.level[0])):
                    transurf.blit(gameMap.level.bg, (x * TILE_SIZE, y * TILE_SIZE))
            
            for e in gameMap.level.particles:
                transurf.blit(e.image, camera.apply(e))
            for e in gameMap.level.underlays:
                transurf.blit(e.image,camera.apply(e))
            camera.update(player)
            
        # update player, draw everything else
            gameMap.level.enemies.update()
            gameMap.level.generators.update()
            gameMap.level.particles.update()
            gameMap.level.projectiles.update()
            gameMap.level.pickups.update(dial)
            gameMap.level.intplatforms.update()
            player.update(aim, jump, up, down, left, right, running, gameMap)
            hud.update()
            
            for e in gameMap.level.pickups:
                transurf.blit(e.image, camera.apply(e))
            for e in gameMap.level.entities:
                transurf.blit(e.image, camera.apply(e))
            for e in gameMap.level.projectiles:
                transurf.blit(e.image, camera.apply(e))
            for e in gameMap.level.overlays:
                transurf.blit(e.image, camera.apply(e))

            pygame.transform.scale2x(transurf, screen)
            hud.draw(screen)
            #pygame.transform.scale(transurf,size, screen)
        pygame.display.flip()
            #pygame.transform.scale(transurf, (1600, 1280), screen)
            #pygame.display.update()
    pygame.quit()


# In[590]:

if __name__ == "__main__":
    main()


# In[ ]:



