import os
import sys
import pygame
import time
import random

# Převod relativní­ cesty vzhledem k tomuto souboru na absolutní­ cestu.
def fix_path(p):
    import os
    return os.path.dirname(os.path.realpath(__file__)) + "/" + p

# Připraví­ pygame (musí­ se zavolat na začátku)
pygame.init()

# Rozměry okna, do kterého budeme kreslit
width = 1500 #960
height = 800 #720
window_size = (width, height)

# Vytvoří­me okno
# -> dostaneme objekt typu Surface, do kterého můžeme kreslit
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Game")

#barvy
black = pygame.Color(0, 0, 0)
blue = pygame.Color(0, 0, 255)
green = pygame.Color(0, 255, 0)
lime = pygame.Color(0, 128, 0)
red = pygame.Color(255, 0, 0)
yellow = pygame.Color(255, 255, 0)
white = pygame.Color(255, 255, 255)
orange = pygame.Color(255, 165, 0)
darkblue = pygame.Color(0, 0, 128)
purple = pygame.Color(128, 0, 128)

#pozadí
background = pygame.image.load("background.jpg").convert()    
background1 = pygame.image.load("background1.jpg").convert() 
background2= pygame.image.load("background2.jpg").convert() 

#ikona hráče
player = pygame.image.load("shooter.png").convert()
player.set_colorkey(white)

playerInv = pygame.image.load("shooter2.png").convert() #lze i shooter3
playerInv.set_colorkey(white)

#kam ho nakreslím
place = int((width/2)-60)
motion = 0
isLeftDown = False
isRightDown = False
isSpaceDown = False

# Vytvoří­me hodiny, které hlídají­ kolik času uplynulo od posledního snímku
clock = pygame.time.Clock()

lives=25
timeWhenLostLife=123
score=0
watch=121

balls=[]
colliders=[]
slugs=[]
slugColliders=[]
distance=400 #pro vzdálenosti střel

# --- Příprava proměnných a tříd pro animaci ---
class Ball:
    global score, balls
    def __init__(self, center, radius, color, new=1, direction = True): #pokud je nová, tak poletí nahoru a znak bude -1, # direction=True poletí doprava, jinak doleva
        self.center = center
        self.radius = radius
        self.color = color
        self.new = new
        self.direction = direction
        if(self.direction==True):
            self.velocity = pygame.Vector2(4.5,int(self.new)*8) #stejná rychlost
        if(self.direction==False):
            self.velocity = pygame.Vector2(-4.5,int(self.new)*8) #stejná rychlost
        self.x = 0
        self.y = 0
        self.gravitation = 0.0025*(100-self.radius)
        balls.append(self) #přidej do pole
        if(self.x==0 and self.y==0): #původní směr
            self.x = self.velocity.x
            self.y = self.velocity.y
        if(self.center[1]<15 or self.center[1]>900 or self.center[0]<-50 or self.center[0]>1600):
            score += self.radius
            balls.remove(self)

    def draw(self): #nakresli
        pygame.draw.circle(screen, self.color, self.center, self.radius)
        self.velocity.y += self.gravitation
    
    def bounce(self): #odraz
        global gravitation
        top = max(height-18*self.radius, 0)
        if self.center[0] < self.radius or self.center[0] > width-self.radius:
            self.velocity.x = -self.velocity.x
        if self.center[1] < top+self.radius or self.center[1] > height-self.radius:
            self.velocity.y = -self.y

    def shift(self):  #posuň
        self.center += self.velocity

class Player: #60x100
    global place, timeWhenLostLife, watch, lives
    def __init__(self,where):
        self.where = where

    def draw(self):
        left=-2
        right=int(width-60)
        if self.where < left+5:
           self.where = left
        if self.where > right-5:
            self.where = right
        if (timeWhenLostLife<=watch+1.5): #+1.5...čas co má imunitu
            screen.blit(playerInv,(self.where, height-100))
        else:
            screen.blit(player,(self.where, height-100))

    def get_downcenter(self):
        return (self.where+30, height)

    def get_undercenter(self):
        return (self.where+30, height-10)
    
    #na kolizi, centerx, centery, radius
    def get_upperCircle(self):
        return (self.where+30, height-75, 26)

    def get_middleCircle(self):
        return (self.where+30, height-40, 25)

    def get_downCircle(self):
        return (self.where+30, height-5, 30)
    
class Slug: #střela
    def __init__(self, color = white):
        global score, slugs
        self.color = color
        self.center = gamer.get_undercenter()
        self.end = gamer.get_downcenter()
        self.velocity = pygame.Vector2(0,-10)
        slugs.append(self)
        score += 10

    def draw(self):
        global slugColliders, slugs
        if(self.center[1]>20):
            pygame.draw.line(screen, self.color, self.center, self.end, width = 2) 
        else: 
            slugs.remove(self)
            slugColliders = []

    def shift(self):  #posuň
        self.center += self.velocity
        #self.end += self.velocity  #aby byla až odspodu

class CircleCollider: #pro balonky
   def __init__(self, centerx, centery, radius):
        self.r = radius
        self.x = centerx
        self.y = centery
        colliders.append(self)
class SlugCollider: #pro střely
   def __init__(self, centerx, centery):
        self.x = centerx
        self.y = centery
        slugColliders.append(self)

def collision(circle1,circle2): #kolize míčku a circle2 bude hráč: [centerx,centery,radius]
    global timeWhenLostLife, watch, lives
    if (timeWhenLostLife<=watch+1.5): #+1.5...čas co má imunitu
        return

    if(abs(circle1.x-circle2[0])>150): #optimalizace+- díky velké vzdálenosti na ose x
       return

    if(abs(circle1.x-circle2[0])<(circle1.r+circle2[2]) and abs(circle1.y-circle2[1])<(circle1.r+circle2[2])):
        lives -= 1
        timeWhenLostLife=watch 
        return True
    else:
        return False
        
#druha kolize pro strelu bude postupně jen dle jejiho vrcholu, nejmensi micek carkovanou siti neproleti bez kolize
def shootingDown(circle1,circle2): #kolize míčku a střely 
    global score
    if(abs(circle1.x-circle2.x)>100): #optimalizace+- díky velké vzdálenosti na ose x
       return
    if(abs(circle1.x-circle2.x)<(circle1.r) and abs(circle1.y-circle2.y)<(circle1.r)):
        score += circle1.r
        return True
    else:
        return False

#zprávy
font1 = pygame.font.SysFont(None, 50, False, True)
font2 = pygame.font.SysFont(None, 40, False, True)

def message(text, color):
    info = font1.render(text, True, color)
    screen.blit(info, (width/3.05, height/2.137))

def message1(text, color):
    info = font1.render(text, True, color)
    screen.blit(info, (width/3.1, height/3.5))

def message2(text, color): 
    info = font1.render(text, True, color)
    screen.blit(info, (width/2.2, height/3.5))

def messFinalLosingScore(text, color): #zpráva o skóre na konci
    info = font2.render(text, True, color)
    screen.blit(info,(width/2.36, height/3.5 + 40))

def messFinalLeftingScore(text, color): #zpráva o skóre po ukončení
    info = font2.render(text, True, color)
    screen.blit(info,(width/2.4, height/3.5 + 40))

def messLives(text, color): #zpráva o životech
    info = font2.render(text, True, color)
    screen.blit(info,(5, 5))

def messScore(text, color): #zpráva o skóre
    info = font2.render(text, True, color)
    screen.blit(info,(width/2.3, 5))

def messTime(text, color): #zpráva o času
    info = font2.render(text, True, color)
    screen.blit(info,(width-135, 5))
    
# Vektor rychlosti kuliček (x, y), v "pixelech za snímek", #středy kuliček, #poloměry, #barva
prvni = Ball((420,680), 30, lime)
druhy = Ball((820,580), 45, purple)
treti = Ball((100,640), 15, darkblue)
ctvrty = Ball((1220,580), 60, orange)
paty = Ball((220,580), 75, yellow)

# --- Začátek animace ---
screen.blit(background1, (0,0))
message("You play the game Bubble Trouble.", orange)
pygame.display.update()
time.sleep(2)

# --- Nekonečná smyčka animace ---
while True:

    gamer = Player(place+motion)

    # --- UPDATE ---

    # Přečteme události, které nastaly od poslední­ho update
    for event in pygame.event.get():
        # --- Konec animace --- A zajistí­me exit při požadavku na zavření okna (křížek)... 
            if(event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                screen.fill(black)
                screen.blit(background2, (0,0))
                message1("You left the game Bubble Trouble.", red)
                messFinalLeftingScore("Your score was: "+str(score), yellow)
                pygame.display.update()
                time.sleep(2)
                pygame.quit()
                print()
                print("You left the game.")
                print("Your score was: "+str(score))
                print("Thank you for playing the game.")
                print()
                os._exit(0) 
                
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    isLeftDown = False
                if event.key == pygame.K_RIGHT:
                    isRightDown = False
                if event.key == pygame.K_SPACE:
                    isSpaceDown = False

            pressed = pygame.key.get_pressed()

            if pressed: 
                if slugs == []:
                    if pressed[pygame.K_SPACE]:
                        s=Slug()
                        isSpaceDown = True
                #elif slugs != []:
                #    if pressed[pygame.K_SPACE] and slugs[-1].center[1]<distance:
                #        s=Slug()
                #        isSpaceDown = True
                

                if((pressed[pygame.K_LEFT] or isLeftDown==True) and int(gamer.where)>=4):
                    motion -= 6
                    isLeftDown = True
                if((pressed[pygame.K_RIGHT] or isRightDown==True) and int(gamer.where)<=int(width-65)):
                    motion += 6
                    isRightDown = True

    if(isLeftDown==True and int(gamer.where)>=4):
        motion -= 6
    if(isRightDown==True and int(gamer.where)<=int(width-65)):
        motion += 6

    #if(isSpaceDown==True and slugs[-1].center[1]<distance):
    #    s=Slug()
    
    if (int(lives)==0 or int(watch)==0 or balls==[]):
      screen.fill(black)
      screen.blit(background2, (0,0))
      message2("You lost.", red)
      messFinalLosingScore("Your score was: "+str(score), yellow)
      pygame.display.update()
      time.sleep(2)
      pygame.quit()
      print()
      print("You lost.")
      print("Your score was: "+str(score))
      print("Thank you for playing the game.")
      print()
      os._exit(0) 


    
    # --- DRAW ---

    # Vyčistíme obrazovku (nastavíme všude černou)
    screen.fill(black)

    screen.blit(background, (0,0))

    
    watch -= 1/60 
    #ve for cyklu všechno kreslení míčků
    colliders = []
    for ball in balls:
        ball.bounce()
        ball.shift()
        ball.draw()
        piece = CircleCollider(ball.center[0], ball.center[1], ball.radius)

    for slug in slugs:
        slug.draw()
        slug.shift()
        net = SlugCollider(slug.center[0], slug.center[1]) #síť střel(y)

    gamer.draw()

    for collider in colliders:
        collision(collider, gamer.get_upperCircle())
    for collider in colliders:
        collision(collider, gamer.get_middleCircle())
    for collider in colliders:
        collision(collider, gamer.get_downCircle())

    for slugCollider in slugColliders:
        for collider in colliders:
            if(shootingDown(collider, slugCollider)):
                new = balls[colliders.index(collider)]
                if (new.radius>15):
                    new1 = Ball(new.center, new.radius-15, new.color, -1, True)
                    new2 = Ball(new.center, new.radius-15, new.color, -1, False)
                    del balls[colliders.index(collider)]
                elif (new.radius==15):
                    del balls[colliders.index(collider)]

    messLives("Lives: "+str(lives), red)
    messScore(f"Score: {score}", green)
    messTime(f"Time: {int(watch)}", orange)

    # Zapíšeme objekt 'screen', "někam", aby se nám zobrazil v okně›
    # (do teď jsme kreslili jen někam do paměti, teď to zobrazíme na obrazovku)
    pygame.display.flip()

    # Budeme spát (nic nedělat) tak dlouho, aby jeden sní­mek trval 1/30 sekundy.
    # To nám zajistí, že nebudeme mí­t 100% vytížení­ CPU, nebudeme kreslit "co nejví­c" snímků.
    clock.tick(60) #FPS


