import os
import sys
import pygame
import time

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

#ikona hráče
player = pygame.image.load("shooter.png").convert()
player.set_colorkey(white)

#kam ho nakreslím
place = int((width/2)-60)
motion = 0
isLeftDown = False
isRightDown = False

gravitation = 0.12 #dodělat gravitaci
# Vytvoří­me hodiny, které hlídají­ kolik času uplynulo od posledního snímku
clock = pygame.time.Clock()


# --- Příprava proměnných a tříd pro animaci ---
class Ball:
    def __init__(self, velocity, center, radius, color):
        self.velocity = velocity
        self.center = center
        self.radius = radius
        self.color = color
        balls.append(self) #přidej do pole

    def draw(self): #nakresli
        pygame.draw.circle(screen, self.color, self.center, self.radius)
        #if self.velocity.y>0: #dolu
         #   self.velocity.y += gravitation
        #if self.velocity.y<0: #nahoru
        self.velocity.y += gravitation
    
    def bounce(self): #odraz
        global gravitation
        top = max(height-18*self.radius, 0)
        if self.center[0] < self.radius or self.center[0] > width-self.radius:
            self.velocity.x = -self.velocity.x
        if self.center[1] < top+self.radius or self.center[1] > height-self.radius:
            self.velocity.y = -self.velocity.y
    def shift(self):  #posuň
        self.center += self.velocity

class Player: #60x100
    global place, motion
    def __init__(self,where):
        self.where = where
    def draw(self):
        left=-2
        right=int(width-60)
        if self.where < left+5:
           self.where = left
        if self.where > right-5:
            self.where = right
        screen.blit(player,(self.where, height-100))
    def get_topcenter(self):
        return (width-self.where-25, height-100)
    def get_uppercenter(self):
        return (width-self.where-25, height-200)

class Slug: #střela
    def __init__(self,color=red):
        self.color=color
    def draw(self):
        pygame.draw.line(screen, self.color, gamer.get_uppercenter(), gamer.get_topcenter(), width=2)#...

#zpráva
font = pygame.font.SysFont(None, 30)

def message(text, color):
    info = font.render(text, True, color)
    screen.blit(info, (width/2-180, height/2))
    
balls=[]

# Vektor rychlosti kuliček (x, y), v "pixelech za snímek", #středy kuliček, #poloměry, #barva
prvni = Ball(pygame.Vector2(5,5), (420,680), 35, orange)
druhy = Ball(pygame.Vector2(6,6), (820,580), 60, purple)
treti = Ball(pygame.Vector2(7,7), (100,640), 25, darkblue)


# --- Nekonečná smyčka animace ---
message("You play the game Bubble Trouble.", green)
pygame.display.update()
time.sleep(2)

while True:

    gamer = Player(place+motion)

    # --- UPDATE ---

    # Přečteme události, které nastaly od poslední­ho update
    for event in pygame.event.get():
        # A zajistí­me exit při požadavku na zavření okna (křížek)
            if event.type == pygame.QUIT:
                screen.fill(black)
                message("You left the game Bubble Trouble.", red)
                pygame.display.update()
                time.sleep(2)
                pygame.quit()
                print("You left the game.")
                os._exit(0) 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    screen.fill(black)
                    message("You left the game Bubble Trouble.", red)
                    pygame.display.update()
                    time.sleep(1)
                    pygame.quit()
                    print("You left the game.")
                    os._exit(0) 

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    isLeftDown = False
                if event.key == pygame.K_RIGHT:
                    isRightDown = False


            pressed = pygame.key.get_pressed()

            if pressed: 
                if pressed[pygame.K_SPACE]:
                    novy = Ball(pygame.Vector2(7,5), (30,680), 30, lime)
                    slug=Slug()
                    slug.draw()
                if(pressed[pygame.K_LEFT] or isLeftDown==True):
                    motion -= 8
                    isLeftDown = True
                if(pressed[pygame.K_RIGHT] or isRightDown==True):
                    motion += 8
                    isRightDown = True

    if isLeftDown==True:
        motion -= 8
    if isRightDown==True:
        motion += 8



    
    # --- DRAW ---

    # Vyčistíme obrazovku (nastavíme všude černou)
    screen.fill(black)

    screen.blit(background, (0,0))

    gamer.draw()
    
    #ve for cyklu všechno kreslení míčků
    gravitation*=1.000002

    for ball in balls:
        ball.bounce()
        ball.shift()
        ball.draw()

    # Zapíšeme objekt 'screen', "někam", aby se nám zobrazil v okně›
    # (do teď jsme kreslili jen někam do paměti, teď to zobrazíme na obrazovku)
    pygame.display.flip()

    # Budeme spát (nic nedělat) tak dlouho, aby jeden sní­mek trval 1/30 sekundy.
    # To nám zajistí, že nebudeme mí­t 100% vytížení­ CPU, nebudeme kreslit "co nejví­c" snímků.
    clock.tick(60)

