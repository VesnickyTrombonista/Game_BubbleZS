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
colors=[]

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

colors.append(black)
colors.append(blue)
colors.append(green)
colors.append(lime)
colors.append(red)
colors.append(yellow)
#colors.append(white)
colors.append(orange)
colors.append(darkblue)
colors.append(purple)

#pozadí
background = pygame.image.load("background.jpg").convert()    
background1 = pygame.image.load("background1.jpg").convert() 
background2= pygame.image.load("background2.jpg").convert() 

#ikona hráče
player = pygame.image.load("shooter.png").convert()
player.set_colorkey(white)

#kam ho nakreslím
place = int((width/2)-60)
motion = 0
isLeftDown = False
isRightDown = False

isSpaceDown = False

# Vytvoří­me hodiny, které hlídají­ kolik času uplynulo od posledního snímku
clock = pygame.time.Clock()

lives=5
timeWhenLostLife=120
score=0
watch=121

balls=[]
slugs=[]
distance=400 #pro vzdálenosti střel

# --- Příprava proměnných a tříd pro animaci ---
class Ball:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color
        self.velocity = pygame.Vector2(4.5,8) #stejná rychlost
        self.x = 0
        self.y = 0
        self.gravitation = 0.0025*(100-self.radius)
        balls.append(self) #přidej do pole
        if(self.x==0 and self.y==0): #původní směr
            self.x = self.velocity.x
            self.y = self.velocity.y

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
    global place
    def __init__(self,where):
        self.where = where
        self.body = pygame.Rect(self.where,height-100,60,100)
    def draw(self):
        left=-2
        right=int(width-60)
        if self.where < left+5:
           self.where = left
        if self.where > right-5:
            self.where = right
        screen.blit(player,(self.where, height-100))

    def get_downcenter(self):
        return (self.where+30, height)

    def get_uppercenter(self):
        return (self.where+30, height-120)

    def collide(self):
        global timeWhenLostLife, watch, lives
        if (timeWhenLostLife<=watch+2): #+2...čas co má imunitu
            pass
        else:
            for color in colors:
                if pygame.sprite.collideany(player,color):
                    lives -= 1
                    timeWhenLostLife=watch

class Slug: #střela
    def __init__(self, color = white):
        global score
        self.color = color
        self.center = gamer.get_uppercenter()
        self.end = gamer.get_downcenter()
        self.velocity = pygame.Vector2(0,-10)
        slugs.append(self)
        score += 10

    def draw(self):
        if(self.center[1]>20):
            pygame.draw.line(screen, self.color, self.center, self.end, width = 2) 
        else: slugs.remove(self)

    def shift(self):  #posuň
        self.center += self.velocity
        #self.end += self.velocity


#zpráva
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
prvni = Ball((420,680), 35, lime)
druhy = Ball((820,580), 60, purple)
treti = Ball((100,640), 20, darkblue)
ctvrty = Ball((1220,580), 72, orange)


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
    
    if (int(lives)==0 or int(watch)==0):
      screen.fill(black)
      screen.blit(background2, (0,0))
      message2("You lost.", red)
      messFinalLosingScore("Your score was: "+str(score), yellow)
      pygame.display.update()
      time.sleep(2)
      pygame.quit()
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

    for ball in balls:
        ball.bounce()
        ball.shift()
        ball.draw()

    for slug in slugs:
        slug.draw()
        slug.shift()

    gamer.draw()

    #gamer.collide()

    messLives("Lives: "+str(lives), red)
    messScore(f"Score: {score}", green)
    messTime(f"Time: {int(watch)}", orange)

    # Zapíšeme objekt 'screen', "někam", aby se nám zobrazil v okně›
    # (do teď jsme kreslili jen někam do paměti, teď to zobrazíme na obrazovku)
    pygame.display.flip()

    # Budeme spát (nic nedělat) tak dlouho, aby jeden sní­mek trval 1/30 sekundy.
    # To nám zajistí, že nebudeme mí­t 100% vytížení­ CPU, nebudeme kreslit "co nejví­c" snímků.
    clock.tick(60) #FPS



