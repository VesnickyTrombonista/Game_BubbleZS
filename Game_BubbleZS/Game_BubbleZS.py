#import knihoven
import os
import sys
import pygame
import time
import random

#převod relativní­ cesty vzhledem k tomuto souboru na absolutní­ cestu.
def fix_path(p):
    import os
    return os.path.dirname(os.path.realpath(__file__)) + "/" + p

#připraví­ pygame (musí­ se zavolat na začátku)
pygame.init()

# rozměry okna na kreslení
width = 1500 #960
height = 800 #720
window_size = (width, height)

# vytvoří­me okno (surface)-kreslení sem
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

#2. ikona hráče
playerInv = pygame.image.load("shooter2.png").convert() #lze i shooter3
playerInv.set_colorkey(white)

#3. ikona hráče
playerFin = pygame.image.load("shooter3.png").convert() #lze i shooter3
playerFin.set_colorkey(white)

#kam ho nakreslím
place = int((width/2)-60)
motion = 0
isLeftDown = False
isRightDown = False
isSpaceDown = False

#vytvoří­me hodiny, které hlídají­ kolik času uplynulo od posledního snímku
clock = pygame.time.Clock()

#proměnné pro hru
lives=5
timeWhenLostLife=203 #oboje o dva více než watch, aby fungovalo
timeWhenShutDown=203
colorOfTime = orange
shutDown=False
score=0
watch=201
level=0
victory=False

balls=[]
colliders=[]
slugs=[]
slugColliders=[]
distance=400 #pro vzdálenosti střel

#třídy pro animaci
class Ball:
    global score, balls #pokud je nová, tak poletí nahoru a znak bude -1, # direction=True poletí doprava, jinak doleva
    def __init__(self, center, radius, color, new=1, direction = True): 
        self.center = center
        self.radius = radius
        self.color = color
        self.new = new
        self.direction = direction
        if(self.direction==True):
            self.velocity = pygame.Vector2(4.5,8) #stejná rychlost
            if(self.new==-1):
                self.velocity = pygame.Vector2(4.5,-8)
        if(self.direction==False):
            self.velocity = pygame.Vector2(-4.5,8)
            if(self.new==-1):
                self.velocity = pygame.Vector2(-4.5,-8)
        self.x = 0
        self.y = 0
        self.gravitation = 0.0025*(100-self.radius)
        balls.append(self) #přidej do pole
        if(self.x==0 and self.y==0): #původní směr
            self.x = self.velocity.x
            self.y = self.velocity.y


    def draw(self): #nakresli
        global score
        if(int(self.center[1])<=32+int(self.radius)): 
            score += self.radius
            balls.remove(self)
        pygame.draw.circle(screen, self.color, self.center, self.radius)
        self.velocity.y += self.gravitation
    
    def bounce(self): #odraz
        global gravitation
        #top = 10 ošetří mi vršek
        if (self.center[0] < self.radius or self.center[0] > width-self.radius):
            self.velocity.x = -self.velocity.x
        if(self.new==-1):
            if (self.center[1] < self.radius): #+top
                self.velocity.y = -self.y
            if(self.center[1] > height-self.radius):
                self.velocity.y = self.y
        else:
            if (self.center[1] < self.radius or self.center[1] > height-self.radius): #+top
                self.velocity.y = -self.y
            
    def shift(self):  #posuň
        self.center += self.velocity

class Player: #60x100
    global place, timeWhenLostLife, watch, lives, victory
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
        if(victory==True):
            screen.blit(playerFin,(self.where, height-100))

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
        self.velocity = pygame.Vector2(0,-14)
        slugs.append(self)

    def draw(self):
        global slugColliders, slugs, shutDown
        if(shutDown==True):
            slugs.remove(self)
            slugs = []
            slugColliders = []
            shutDown=False
            return
        if(self.center[1]>20):
            pygame.draw.line(screen, self.color, self.center, self.end, width = 2) 
        else: 
            slugs.remove(self)
            slugColliders = []
            slugs = []

    def shift(self):  #posuň
        self.center += self.velocity
        #self.end += self.velocity  #nebyla by až odspodu

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

def shootingDown(circle1,circle2): #kolize míčku a střely 
    global score, watch, timeWhenShutDown
    if(timeWhenShutDown<=watch+0.2): #aby se stihly posunout menší míčky
        return

    if(abs(circle1.x-circle2.x)>100): #optimalizace+- díky velké vzdálenosti na ose x
       return

    if(abs(circle1.x-circle2.x)<(circle1.r) and abs(circle1.y-circle2.y)<(circle1.r)):
        score += circle1.r
        return True
    else:
        return False


#zprávy ve hře
font1 = pygame.font.SysFont("Ariel", 50, False, True)
font2 = pygame.font.SysFont(None, 40, False, True)

def message(text, color):
    info = font1.render(text, True, color)
    screen.blit(info, (width/3.07, height/2.137))

def message1(text, color):
    info = font1.render(text, True, color)
    screen.blit(info, (width/3.1, height/3.5))

def message2(text, color): 
    info = font1.render(text, True, color)
    screen.blit(info, (width/2.2, height/3.5))

def message3(text, color): 
    info = font1.render(text, True, color)
    screen.blit(info, (50, height/2-70))

def message4(text, color): 
    info = font1.render(text, True, color)
    screen.blit(info, (50, height/2-20))

def message5(text, color): 
    info = font1.render(text, True, color)
    screen.blit(info, (50, height/2+30))

def message6(text, color): 
    info = font1.render(text, True, color)
    screen.blit(info, (50, height/2+150))

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
    screen.blit(info,(width/3.5, 5))

def messTime(text, color): #zpráva o času
    info = font2.render(text, True, color)
    screen.blit(info,(width-135, 5))

def messLevel(text, color): #zpráva o času
    info = font2.render(text, True, color)
    screen.blit(info,(width/1.75, 5))
    
#vektor rychlosti kuliček (x, y), v "pixelech za snímek", střed, poloměry barva,1-dolu, -1 nahoru, True vpravo, False vlevo
#přidání v cyklu
#first = Ball((100,640), 15, darkblue, 1, True)
#second = Ball((420,680), 30, lime, 1, True)
#third = Ball((820,580), 45, purple, 1, True)
#fourth = Ball((1220,580), 60, orange, 1, True)
#fifth = Ball((220,580), 75, yellow, 1, True)

#začátek animace
screen.blit(background1, (0,0))
message("You play the game Bubble Trouble.", orange)
pygame.display.update()
time.sleep(2)

#pravidla
screen.fill(black)
screen.blit(background1, (0,0))
messLives("Lives: "+str(lives), red)
messScore(f"Score: {score}", green)
messTime(f"Time: {int(watch)}", colorOfTime)
messLevel(f"Level: {int(level)}", blue)
message3("Controls: <-  -> , space - shooting, esc - left the game", black)
message4("You can see your lives, score, level and time at the top", black)
message5("If the bubble touches the line, it will be destroyed", black)
message6("Press SPACE to continue . . . ", red)
pygame.draw.line(screen, purple, (0,32), (1500,32), width = 4)
pygame.display.update()

#čekání na začátek
while isSpaceDown==False:
    time.sleep(0.1)
    for event in pygame.event.get():
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            isSpaceDown=True
isSpaceDown=False

#nekonečná hlavní smyčka animace
while True:               
    #přečteme události, tj. změny od poslední­ho update=new update
    for event in pygame.event.get():
        #ukončení animace a zajistí­me exit při požadavku na zavření okna (křížek)... 
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
                
            #zmáčknutí kláves
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
                    if pressed[pygame.K_SPACE]: #střílí pomalu, občas ne
                        s=Slug()
                        isSpaceDown = True

                if((pressed[pygame.K_LEFT] or isLeftDown==True) and int(gamer.where)>=4):
                    motion -= 6
                    isLeftDown = True

                if((pressed[pygame.K_RIGHT] or isRightDown==True) and int(gamer.where)<=int(width-65)):
                    motion += 6
                    isRightDown = True

                #cheat
                if pressed[pygame.K_KP0]:
                    level=10

    if(isLeftDown==True and int(gamer.where)>=4):
        motion -= 6
    if(isRightDown==True and int(gamer.where)<=int(width-65)):
        motion += 6
    if(isSpaceDown and slugs==[]):
        s=Slug()

    #konec, bez životů/času
    if (int(lives)==0 or int(watch)==0):
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
    
    #draw

    #vyčistíme obrazovku (nastavíme všude černou) a pak vše na to
    screen.fill(black)
    screen.blit(background, (0,0))

    watch -= 1/60 

    #ve for cyklu všechno kreslení míčků a střel, hráč, kolize
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

    #hráč
    gamer = Player(place+motion)
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
                shutDown=True
                timeWhenShutDown=watch
                new = balls[int(colliders.index(collider))]
                slugColliders = []
                slugs = []
                if (int(new.radius)>15):
                    new1 = Ball((new.center[0]+2, new.center[1]+1), new.radius-15, new.color, -1, direction=True)
                    new2 = Ball((new.center[0]-2, new.center[1]+1), new.radius-15, new.color, -1, direction=False)
                    del balls[int(colliders.index(collider))]
                    del new
                    del collider
                elif (int(new.radius)==15):
                    del balls[int(colliders.index(collider))]
                    del new
                    del collider

    #zprávy v hlavičce
    messLives("Lives: "+str(lives), red)
    messScore(f"Score: {score}", green)
    messLevel(f"Level: {int(level)}", blue)
    messTime(f"Time: {int(watch)}", colorOfTime)
    if watch<20:
        colorOfTime = red

    pygame.draw.line(screen, purple, (0,32), (1500,32), width = 4) #čára oddělující skóre a je to top, kde se bubliny rozbijí
    
    #levly
    if(balls==[]):

        #začátek
        level += 1
        screen.fill(black)
        screen.blit(background, (0,0))
        messLives("Lives: "+str(lives), red)
        messScore(f"Score: {score}", green)
        messTime(f"Time: {int(watch)}", colorOfTime)
        messLevel(f"Level: {int(level)}", blue)
        pygame.draw.line(screen, purple, (0,32), (1500,32), width = 4)
        
        if(level==1):
            first = Ball((100,650), 15, darkblue, 1, True)
        if(level==2):
            second = Ball((220,550), 30, lime, 1, True)
        if(level==3):
            third = Ball((1320,300), 45, purple, 1, False)
        if(level==4):
            first1 = Ball((100,500), 15, darkblue, 1, True)
            first2 = Ball((200,500), 15, darkblue, 1, True)
            second1 = Ball((1120,500), 30, lime, 1, True)
            second2 = Ball((1220,500), 30, lime, 1, True)
        if(level==5):
            fourth = Ball((111,200), 60, orange, 1, True)
        if(level==6):
            fourth1 = Ball((1220,300), 60, orange, 1, True)
            fourth2 = Ball((220,300), 60, orange, 1, False)
        if(level==7):
            lives += 1
            fifth = Ball((220,300), 75, yellow, 1, True)
        if(level==8):
            fifth1 = Ball((220,200), 75, yellow, 1, True)
            fifth2 = Ball((1220,200), 75, yellow, 1, False)
        if(level==9):
            third1 = Ball((100,250), 45, purple, 1, True)
            third2 = Ball((300,250), 45, purple, 1, True)
            third3 = Ball((720,250), 45, purple, 1, True)
            third4 = Ball((1100,250), 45, purple, 1, True)
            third5 = Ball((1300,250), 45, purple, 1, True)
        if(level==10):
            lives += 1
            fourth1 = Ball((1220,300), 60, orange, 1, True)
            fourth2 = Ball((220,300), 60, orange, 1, False)
            fourth3 = Ball((1020,300), 60, orange, 1, True)
            fourth4 = Ball((420,300), 60, orange, 1, False)

        #...případné další levly

        for ball in balls:
            ball.draw()
        motion = 0
        gamer = Player(place+motion)
        gamer.draw()        
        pygame.display.flip()
        time.sleep(2)

        #konec
        if (level==11):
            time.sleep(0)
            screen.fill(black)
            screen.blit(background2, (0,0))
            message2("You won.", red)
            messFinalLosingScore("Your score was: "+str(score), yellow)
            victory=True
            gamer.draw()
            pygame.display.update()
            time.sleep(2)
            pygame.quit()
            print()
            print("You win.")
            print("Your score was: "+str(score))
            print("Thank you for playing the game.")
            print()
            os._exit(0)
            
    #zapíšeme objekt 'screen', "někam", aby se nám zobrazil v okně›
    #do teď jsme kreslili jen někam do paměti, teď to zobrazíme na obrazovku
    pygame.display.flip()

    #spaní, aby jeden sní­mek trval 1/60 sekundy
    #nebude 100% vytížení­ CPU, nebudeme kreslit "co nejví­c" snímků
    clock.tick(60) #FPS


