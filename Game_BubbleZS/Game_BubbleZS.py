import os
import sys
import pygame
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


# Načteme obrázek míčku, opět dostaneme objekt typu Surface
# ! pozor: musíme program spouštět ze stejné složky, ve které máme obrázek, jinak se nenačte (bez fix_path) ! 
# - convert() mění­ vnitřní­ reprezentaci uložení­ obrázku, aby se to nemuselo dělat až při vykreslení -> rychlejší hra.
#ball_image1 = pygame.image.load(fix_path("ball.png")).convert()
# ball = pygame.image.load("ball.png")
# ball_image2 = pygame.image.load(fix_path("ball.png")).convert()

# Vyrobí­me si obdélní­k kolem míčku -- později ho použijeme pro animaci a detekci kolizí.
# -> dostaneme objekt typu Rect (0, 0, w, h), kde w, h jsou rozměry obrázku (jako int)
# ball_rect1 = ball_image1.get_rect()
# print("Ball rect:", ball_rect1) 
# ball_rect2 = ball_image2.get_rect()
# print("Ball rect:", ball_rect2)
# ball_rect3 = ball_image1.get_rect()
# print("Ball rect:", ball_rect3)

background = pygame.image.load("background.jpg").convert() #...vybrat správný obrázek


player = pygame.image.load("shooter.png").convert()
player.set_colorkey(white)


#velocity = pygame.Vector2(8, 11)

#image.set_colorkey((255, 0, 0)) klíč, který nevykreslí barvu pozadí
# New width and height will be (50, 30).
#IMAGE_SMALL = pg.transform.scale(IMAGE, (50, 30))
# Rotate by 0 degrees, multiply size by 2.
#IMAGE_BIG = pg.transform.rotozoom(IMAGE, 0, 2)



# Vytvoří­me hodiny, které hlídají­ kolik času uplynulo od posledního snímku
clock = pygame.time.Clock()


# --- Příprava proměnných pro animaci ---
class Ball:
    def __init__(self, velocity, center, radius, color):
        self.velocity = velocity
        self.center = center
        self.radius = radius
        self.color = color
        balls.append(self) #přidej do pole

    def draw(self): #nakresli
        pygame.draw.circle(screen, self.color, self.center, self.radius)
    
    def bounce(self): #odraz
        top = max(height-12*self.radius, 0)
        if self.center[0] < self.radius or self.center[0] > width-self.radius:
            self.velocity.x = -self.velocity.x
        if self.center[1] < top+self.radius or self.center[1] > height-self.radius:
            self.velocity.y = -self.velocity.y

    def shift(self):  #posuň
        self.center += self.velocity

class Player: #108x165
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def draw(self):
        screen.blit(player,(self.x, self.y))
    def get_topcenter(self):
        return (width-self.x-50,height-165)
    def get_uppercenter(self):
        return (width-self.x-150,height-165)
    #if ball_rect.left < 0 or ball_rect.right > width:
     #   velocity.x = -velocity.x
    #if ball_rect.top < 0 or ball_rect.bottom > height:
     #   velocity.y = -velocity.y

class Slug: #střela
    def __init__(self,color=red):
        self.color=color
    def draw(self):
        pygame.draw.line(screen, self.color, Player.get_uppercenter(), PLayer.get_topcenter(),width=2)

    
balls=[]

# Vektor rychlosti kuliček (x, y), v "pixelech za snímek", #středy kuliček, #poloměry, #barva
prvni = Ball(pygame.Vector2(6,6), (420,680), 35, orange)
druhy = Ball(pygame.Vector2(7,7), (820,580), 70, purple)
treti = Ball(pygame.Vector2(8,8), (100,640), 25, darkblue)


# --- Nekonečná smyčka animace ---
while True:
    # --- UPDATE ---

    # Přečteme události, které nastaly od poslední­ho update
    for event in pygame.event.get():
        # A zajistí­me exit při požadavku na zavření okna (křížek)
            if event.type == pygame.QUIT:
                pygame.quit()
                print("You left the game.")
                os._exit(0) 

            if event.type == pygame.KEYDOWN: # or event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    novy = Ball(pygame.Vector2(7,5), (30,680), 30, lime)
                if event.key == pygame.K_SPACE:
                    slug=Slug()
    #space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]



    
    # --- DRAW ---

    # Vyčistíme obrazovku (nastavíme všude černou)
    screen.fill(black)


    #player = Player(200,200)
    screen.blit(background, (0,0))
    screen.blit(player,((width/2)-80, height-160))

    #ve for cyklu všechno kreslení

    for ball in balls:
        ball.bounce()
        ball.shift()
        ball.draw()

    # Zapíšeme objekt `screen`, "někam", aby se nám zobrazil v okně›
    # (do teď jsme kreslili jen někam do paměti, teď to zobrazíme na obrazovku)
    pygame.display.flip()

    # Budeme spát (nic nedělat) tak dlouho, aby jeden sní­mek trval 1/30 sekundy.
    # To nám zajistí, že nebudeme mí­t 100% vytížení­ CPU, nebudeme kreslit "co nejví­c" snímků.
    clock.tick(60)

