# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
from numpy.lib.stride_tricks import DummyArray
import pygame
import random
import os
import math

from pygame import draw
import numpy as np
import random
from pygame import time 

from pygame.draw import rect

pygame.init()

#-----------------------------------------------------------------------------------------
# CONSTANTES ET VARIABLES
#-----------------------------------------------------------------------------------------

WIDTH = 480
HEIGHT = 600
FPS = 60

# dimensions barre d'infos
INFO_H = 80
INFO_M = 20

# définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TURQUOISE = (105, 132, 145)

# initialisation de pygame et création de la fenêtre
pygame.init()
pygame.mixer.init()
#définition de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT + INFO_H))
#nom de la fenêtre
pygame.display.set_caption("C'est balaud")
clock = pygame.time.Clock()
POWERUP_TIME = 5000

# mise en place des ressources
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'Images')
# chargement des graphiques pour le jeu
background = pygame.image.load(os.path.join(img_folder, "fond.png")).convert()
background_rect = background.get_rect()

bullet_img = pygame.image.load(os.path.join(img_folder, 'laser.png')).convert()
player_img = pygame.image.load(os.path.join(img_folder, "main.png")).convert_alpha()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
#création d'une liste comportant diverses images de météorites
meteor_images = []
boss_images = []
meteor_images.append(pygame.image.load(os.path.join(img_folder, 'aléa.png')).convert_alpha())
boss_images.append(pygame.image.load(os.path.join(img_folder, 'superaléa.png')).convert_alpha())

#Mise en place des ressources, des sprites pour l'animation des différentes explosions des météorites   
explosion_anim = {}
#liste pour les grosses météorites
explosion_anim['lg'] = []
#liste pour les petites
explosion_anim['sm'] = []
#définition de la liste servant pour l'animation de l'explosion du player
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    #définition de l'explosion pour le player
    explosion_anim['player'].append(img)

#définition des images à utiliser pour les powerups
powerup_images = {}
powerup_images['gun'] = pygame.image.load(os.path.join(img_folder, 'bolt_gold.png')).convert()

# Chargement de tous les musiques et effets sonores
snd_dir = os.path.join(game_folder, 'snd')
gun_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'gun.wav'))
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pew.wav'))
player_explosion_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'explosion.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_dir, snd)))
pygame.mixer.music.load(os.path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.mp3'))
pygame.mixer.music.set_volume(0.01)
gun_sound.set_volume(0.01)
shoot_sound.set_volume(0.01)
player_explosion_sound.set_volume(0.01)
for expl_sound in expl_sounds:
    expl_sound.set_volume(0.01);

tab_degat_arme = []
tab_freq_app = []
tab_accuracy = []

#liste des aleas
listeAlea = [
    ["Votre appartement a pris feu", -50, "money"],
    ["Votre petit(e)-ami(e) romp avec vous", -3, "time"],
    ["Votre mère décide de vous rendre visite", +100, "money"],
    ["La banque décide de saisir vos biens", -100, "money"],
    ["Vous avez pris un coup de vieux", -1, "time"]
]

listeDiff = [
    ["Burn-out à cause de l'IMAC", -3, "time"],
    ["On vous a viré comme un malpropre", -300, "money"],
    ["Vous n'auriez pas dû manger ça...", -5, "time"]
]

difficulty = 0

#-----------------------------------------------------------------------------------------
# CLASSES
#-----------------------------------------------------------------------------------------

#création d'un sprite avec le vaisseau
class Player(pygame.sprite.Sprite):
    def __init__(self):
        #self est une convention de python pour le premier paramètre d'une instance
        pygame.sprite.Sprite.__init__(self)
         
        #définition de la taille du rectangle
        self.image = pygame.Surface((31, 104)) # 50, 40
        #couleur de l'élément
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        #définition du rayon de la surface du joueur
        self.radius = 32 # ?
        #définition de la position du rectangle (vaisseau)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT # HEIGHT - 10
        #définition de la vitesse
        self.speedx = 0
        #définition de la valeur du bouclier
        self.shield = 100
        #mise en place d'une image pour le joueur
        self.image= player_img
        self.image.set_colorkey(BLACK)
        self.shoot_delay = 250
        self.hidden = False
        self.last_shot = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

        #définition de la précision, attaque, argent
        
        if(difficulty == 2) :
            self.accuracy = 0.3
            self.interval = 30
        else :
            self.accuracy = 0.6
            self.interval = 20
        self.attack = 30
        self.money = 5000
        self.strength = 30

    def update(self):
        #pause pour les bonus
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        
        #permet de révéler le joueur si il est caché
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            
        self.speedx = 0
        #Création d'une variable quand la touche est pressée
        event = pygame.key.get_pressed()
        #Déplace l'objet vers la gauche quand la touche gauche est pressée
        if event[pygame.K_LEFT] : 
            self.speedx -= 5
        
        #Déplace l'objet vers la droite quand la touche droite est pressée
        if event[pygame.K_RIGHT] : 
            #On incrémente de 5
            self.speedx += 5
        self.rect.x +=self.speedx
        #Lance un rayon laser
        if event[pygame.K_SPACE]:
            player.setAttack()
            self.shoot()
    
        #Garder l'objet dans l'écran
        if self.rect.left < 0 :
            self.rect.left = 0
        if self.rect.right > WIDTH :
            self.rect.right = WIDTH
    
    #définition d'une fonction pour fixer les propriétés du bonus        
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    #ajout Bernoulli
    #définition de la fonction permettant de tirer    
    def shoot(self):
        now = pygame.time.get_ticks()
        r = random.random()
        tab_accuracy.append(r)
        if r > self.accuracy :
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                #production d'une météorite si le bonus = 1
                if self.power == 1:
                    bullet = Bullet(self.rect.centerx-2, self.rect.top) # self.rect.centerx
                    bullet.attack = player.attack
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    shoot_sound.play()
                #production de deux météorites si le bonus est > 1
                if self.power >= 2:
                    bullet1 = Bullet(self.rect.left, self.rect.centery)
                    bullet2 = Bullet(self.rect.right, self.rect.centery)
                    bullet1.attack = player.attack
                    bullet2.attack = player.attack
                    all_sprites.add(bullet1)
                    all_sprites.add(bullet2)
                    bullets.add(bullet1)
                    bullets.add(bullet2)
                    shoot_sound.play()
        
    def hide(self):
        # cache le joueur temporairement
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def buyAccuracy(self):
        cost = round(np.exp(self.accuracy*5))
        if(prev_time < message.time+1500):
            return
        if(cost > self.money):
            message.text = "Manque "+str(cost-self.money) +" pts"
        elif(self.accuracy>=0.95):
            message.text = "Précision maximale. Amélioration impossible"
        else:
            self.accuracy+= 0.05
            self.accuracy = round(self.accuracy, 2)
            self.money -= cost
            message.text = "+0.05 en précision"
        
        if(prev_time > message.time+1500):
            message.time = pygame.time.get_ticks()
            all_sprites.add(message)
    
    def buyStrength(self):
        if(prev_time < message.time+1500):
            return
        cost = round(np.exp(self.strength*0.1))
        if(cost > self.money):
            message.text = "Manque " + str(cost-self.money) + " pts"
        else:
            self.strength+= 5
            self.money -= cost
            message.text = "+5 en force"

        message.time = pygame.time.get_ticks()
        all_sprites.add(message)

    #AJOUTE
    #donne une valeur aléatoire d'attaque entre 10 ee 100 par pas de 10 selon une loi uniforme
    def setAttack(self):
        lower_attack = self.strength-self.interval
        if(lower_attack< 0):
            lower_attack = 0
        results = np.arange(lower_attack, self.strength+(self.interval + 5), 5)
        probabilities = np.ones(len(results)) / len(results)
        r = random.random()
        self.attack = getResult(r, results, probabilities)
        tab_degat_arme.append(self.attack)
        return self.attack

class Message(pygame.sprite.Sprite):
    def __init__(self):
        #self est une convention de python pour le premier paramètre d'une instance
        pygame.sprite.Sprite.__init__(self)
        
        #définition de la taille du rectangle
        self.image = pygame.Surface((WIDTH-100, 50))
        
        #couleur de l'élément
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.rect.x = WIDTH/2-self.rect.width/2
        self.rect.y = -self.rect.height+HEIGHT/2
        self.last_update = pygame.time.get_ticks()

        self.text = "Nothing"
        self.time = -10000

#création d'un sprite pour l'astéroïde          
class Ennemi(pygame.sprite.Sprite):
    def __init__(self, max_health, attack, images):
        #self est une convention de python pour le premier paramètre d'une instance
        pygame.sprite.Sprite.__init__(self)
        
        #définition de la taille du rectangle
        self.image = pygame.Surface((30, 40))
        
        #couleur de l'élément
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        #définition de la position du rectangle (vaisseau)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-80,-20)
        self.speedy = random.randrange(1,8)
        self.speedx = random.randrange(-3,3)
        #choisit une image dans la liste et l'attribut à la météorite créée
        self.image_orig =  images[0] # random.choice(images)
        self.image.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        
        #AJOUTE
        #définition des points d'attaque et des points de vie
        self.max_health = max_health
        self.health = max_health
        self.attack = attack
        # self.attack = 20

    #permet de faire tourner la météorite    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

    #AJOUTE
    #dessine la barre de vie
    def draw_bar(self):
        draw_shield_bar(screen, self.rect.x, self.rect.y - 15 , self.health, self.max_health)
        draw_text(screen, str(ennemi.health), 18, WHITE, self.rect.x + 120, self.rect.y - 20)

#Création de sprites pour les tirs           
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        #On remplace le rectangle jaune par une image
        self.image= bullet_img
        #self.image = pygame.Surface((10, 20))
        self.image.set_colorkey(BLACK) 
        #self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        self.attack = 0
        

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()
  
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

#création de sprites pour les bonus                
class Bonus(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'gun'
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()

class Text(pygame.sprite.Sprite):
    def __init__(self, text, size, color, width, height):
        # Call the parent class (Sprite) constructor  
        pygame.sprite.Sprite.__init__(self)
    
        self.font = pygame.font.SysFont("Arial", size)
        self.textSurf = self.font.render(text, 1, color)
        # to get a transparent rect
        self.image = pygame.Surface((width, height), pygame.SRCALPHA) 
        self.image.fill((255,255,255,0)) # notice the alpha value in the color
        screen.blit(self.image, (0,0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, [width/2 - W/2, height/2 - H/2])
        self.time = -1

#-----------------------------------------------------------------------------------------
# METHODES
#-----------------------------------------------------------------------------------------

#définition d'une nouvelle météorite
def newEnnemi():
    m = createMinion()
    all_sprites.add(m)
    Ennemis.add(m) 

#définition d'une barre de progression de la qualité du bouclier
def draw_shield_bar(surf, x, y, pct, max):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = pct * BAR_LENGTH / max
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_message(text):
    pygame.draw.rect(screen, TURQUOISE, pygame.Rect(50, 50-HEIGHT/2, WIDTH-100, 100))
    draw_text(screen, text, 18, WHITE, WIDTH/2, HEIGHT/2)

#définition d'un écran explicatif
def show_go_screen():
    global difficulty
    global listeAlea
    screen.blit(background, background_rect)
    h = 20+HEIGHT / 4
    pygame.draw.rect(screen, TURQUOISE, pygame.Rect(0, 100, WIDTH, HEIGHT+INFO_H-200))
    draw_text(screen, "C'EST BALAUD", 64, WHITE, WIDTH / 2, h)
    draw_text(screen, "Lassé des aléas de la vie, vous décidez de prendre", 22, WHITE, WIDTH / 2, h+120)
    draw_text(screen, "en main votre destin ! Terrassez-les tous !", 22, WHITE, WIDTH / 2, 150+h)
    draw_text(screen, "Flèches pour se déplacer, Espace pour tirer", 22, WHITE, WIDTH / 2, 250+h)
    draw_text(screen, "Appuyez sur 2 pour choisir le mode HELL", 18, WHITE, WIDTH / 2, 300+h)
    draw_text(screen, "Appuyez sur 1 pour choisir le mode normal", 18, WHITE, WIDTH / 2, 350+h)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_KP2:
                    difficulty = 2
                    listeAlea += listeDiff
                    waiting = False
                else :
                    difficulty = 1
                    waiting = False

def createMinion():
    return Ennemi(50, 20, meteor_images)

def createBoss():
    return Ennemi(400, 50, boss_images)


def afficheAlea(player, message) :
    global duration_game
    liste = getUniformPond(listeAlea)
    message.text = liste[0]
    if liste[2] == "time" :
        duration_game += liste[1]

    else :
        if(player.money + liste[1] < 0):
            player.money = 0
        else : 
            player.money += liste[1] 

def pause() : 
    loop = 1
    while loop : 
        for event in pygame.event.get() : 
            if event.type == pygame.QUIT:
                loop = 0
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_ESCAPE:
                    loop == 0
                if event.key == pygame.K_SPACE:
                    loop == 0
        pygame.display.update()
        clock.tick(60)
#-----------------------------------------------------------------------------------------
# METHODES MATHEMATIQUES
#-----------------------------------------------------------------------------------------

def getResult(random, array_results, array_probabilities):
    sum = 0
    i = -1
    index = -1
    while(sum<=1 or index==-1):
        if(random <= sum):
            index = i
            break
        i+=1
        #print(i)
        sum+=array_probabilities[i]

    return array_results[index]

#AJOUTE
def fact(n):
    F = 1
    for k in range(1, n+1):
        F *= k
    return F

#AJOUTE
def getProbabilitiesPoisson(para1):
    probabilities = []
    results = []
    i=0
    sum=0
    while("la probabilité est différente de 0"):
        proba = np.exp(-para1)*pow(para1, i)/fact(i)
        if(sum==1):
            break
        probabilities.append(proba)
        results.append(i)
        sum += proba
        i+=1
    return probabilities, results

def getContinuousUniform(a, b):
    results = np.arange(a, b, 1)
    probabilities = np.ones(len(results)) / (b-a)
    return probabilities, results

def newBoss():
    m = createBoss()
    all_sprites.add(m)
    Ennemis.add(m) 

def convertMsecToMinSec(millis):
    seconds=round(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    #hours=(millis/(1000*60*60))%24
    return str(minutes) + ":" + str(seconds)

def getUniformPond(liste):
    r = random.random()
    listeProb = [1/len(liste)] * len(liste)
    return getResult(r, liste, listeProb)

def getExponentialLaw(para1) :
    probabilities = []
    results = []
    i=1
    sum=0
    while("la probabilité est différente de 0"):
        results.append(i)
        proba = - np.exp(-para1 * (i)) + np.exp(-para1 * (i-1))
        probabilities.append(proba)
        sum += proba
        print(i, "p = ", proba, "sum =", sum)
        i+=1
        if(sum>=1 or proba <= pow(10, -8)):
            break
    return getResult(random.random(), results, probabilities)


#-----------------------------------------------------------------------------------------
# STATISTIQUES (ESPERANCE ET ECART-TYPE)
#-----------------------------------------------------------------------------------------

def statsPoisson(para1):
    expected_val = para1
    standard_der = np.sqrt(para1)
    return expected_val, standard_der

def statsContinuousUniform(a, b):
    expected_val = (b+a)/2
    standard_der = (b-a)/np.sqrt(12)
    return expected_val, standard_der

def statsUniform(n, a, b):
    expected_val = (b+a)/2
    standard_der = np.sqrt((pow(n, 2)-1)/12)
    return expected_val, standard_der

def statsBernouilli(p):
    expected_val = p
    standard_der = np.sqrt(p*(1-p))
    return expected_val, standard_der

def statsExp(para1):
    expected_val = 1/para1
    standard_der = 1/para1
    return expected_val, standard_der

#définition d'unécran explicatif
def show_stats_screen():
    ev1, sd1 = statsBernouilli(player.accuracy) # Arme fontionne ou pas  

    lower_attack = player.strength-20
    if(lower_attack< 0):
        lower_attack = 0
    array = np.arange(lower_attack, player.strength+25, 5)
    ev2, sd2 = statsUniform(len(array), array[0], array[len(array)-1]) # Dégâts de l'arme

    ev3, sd3 = statsExp(1/60) # Durée de vie initiale de l'arme en sec

    ev4, sd4 = statsPoisson(1) # Fréquence moyenne d'apparition des aléas, 1 par sec
    ev5, sd5 = statsContinuousUniform(init_duration_game/2, init_duration_game) # Temps d'apparition des boss

    m1 = sum(tab_accuracy) / len(tab_accuracy)
    m2 = sum(tab_degat_arme) / len(tab_degat_arme)
    m4 = sum(tab_freq_app) / len(tab_freq_app)

    pygame.draw.rect(screen, TURQUOISE, pygame.Rect(0, 0, WIDTH, HEIGHT+INFO_H))

    d = 40
    draw_text(screen, "Statistiques", 64, WHITE, WIDTH / 2, d-60 + HEIGHT / 13)
    draw_text(screen, "Fonctionnement de l'arme", 22, WHITE, WIDTH / 2, d+HEIGHT*2/13)
    draw_text(screen, "Espérance : " + str(round(ev1, 2)) + "  Ecart-type : " + str(round(sd1, 2)) + "   Moyenne réelle : " + str(round(m1, 2)), 18, WHITE, WIDTH / 2, d-10+HEIGHT*3/13)
    draw_text(screen, "Dégâts de l'arme", 22, WHITE, WIDTH / 2, d+HEIGHT*4/13)
    draw_text(screen, "Espérance : " + str(round(ev2, 2)) + "   Ecart-type : " + str(round(sd2, 2)) + "   Moyenne réelle : " + str(round(m2, 2)), 18, WHITE, WIDTH / 2, d-10+HEIGHT*5/13)
    draw_text(screen, "Durée de vie intiale de l'arme (en sec)", 22, WHITE, WIDTH / 2, d+HEIGHT*6/13)
    draw_text(screen, "Espérance : " + str(round(ev3, 2)) + "   Ecart-type : " + str(round(sd3, 2)) + "   Valeur réelle : " + str(init_duration_game), 18, WHITE, WIDTH / 2, d-10+HEIGHT*7/13)
    draw_text(screen, "Fréquence d'apparition des aléas (par sec)", 22, WHITE, WIDTH / 2, d+HEIGHT*8/13)
    draw_text(screen, "Espérance : " + str(round(ev4, 2)) + "   Ecart-type : " + str(round(sd4, 2)) + "   Moyenne réelle : " + str(round(m4, 2)), 18, WHITE, WIDTH / 2, d-10+HEIGHT*9/13)
    draw_text(screen, "Temps d'apparition des boss (en sec)", 22, WHITE, WIDTH / 2, d+HEIGHT*10/13)
    draw_text(screen, "Espérance : " + str(round(ev5, 2)) + "   Ecart-type : " + str(round(sd5, 2)) + "   Valeur réelle : " + str(apparition_boss), 18, WHITE, WIDTH / 2, d-10+HEIGHT*11/13)
    draw_text(screen, "Appuyer sur Entrer du pavé numérique pour recommencer une partie", 18, WHITE, WIDTH / 2, d+20+HEIGHT*12/13)

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_KP_ENTER:
                    waiting = False


#création de groupes pour lancer les éléments dans la fenêtre
all_sprites = pygame.sprite.Group()
powerups = pygame.sprite.Group()
Ennemis= pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
ennemi = createMinion() 

score=0
#Met la musique de fond en boucle
pygame.mixer.music.play(loops=-1)

#appel d'une police et mise en place de celle-ci
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, color, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


#-----------------------------------------------------------------------------------------
# BOUCLE DU JEU
#-----------------------------------------------------------------------------------------

game_over = True
running = True
prev_time = pygame.time.get_ticks()
show_stats = False
pause = False

while running:
    #si le joueur a perdu et souhaite rejouer, les éléments sont recréés
    if show_stats:
        show_stats_screen()
    if game_over:
        show_go_screen()
    
        #AJOUTE
        tab_degat_arme.append(player.attack)
        init_duration_game = getExponentialLaw(1/60) # durée de vie initiale de l'arme en sec
        duration_game = init_duration_game # durée de vie de l'arme en secondes pourra être augmentée par des âchats
        # Temps après quoi le boss apparaît
        r_boss = random.random()
        probabilities_boss, results_boss = getContinuousUniform(round(duration_game/2), duration_game) #en secondes, 
        start = pygame.time.get_ticks()
        apparition_boss = getResult(r_boss, results_boss, probabilities_boss)

        show_stats = False
        game_over = False
        all_sprites = pygame.sprite.Group()
        Ennemis = pygame.sprite.Group() #AJOUTE
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        message = Message()
        bullets_damages = pygame.sprite.Group()
        all_sprites.add(player)
        # for i in range(8):
        #     newEnnemi()
        score = 0
    #continue de jouer la boucle à la bonne vitesse
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # vérifie si la fenêtre se ferme
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            #Achète une amélioration de précision
            if event.key == pygame.K_KP6:
                pause()
            #Achète une amélioration de temps
            if event.key == pygame.K_KP0:
                if(pause == True):
                    pause = False
                else:
                    pause = True
            if event.key == pygame.K_KP3:
                cost = 100
                if(prev_time >= message.time+1500):

                    if(cost > player.money):
                        message.text = "Manque "+str(cost-player.money)+" pts"
                    else:
                        duration_game += 10 #en sec
                        player.money -= cost
                        message.text = "+10s"
                        
                    if(prev_time > message.time+1500):
                        message.time = pygame.time.get_ticks()
                        all_sprites.add(message)


    if(pygame.time.get_ticks() - start >= duration_game*1000):
        show_stats = True
        game_over = True
    
    #AJOUTE
    #Apparition des ennemis à une fréquence moyenne de 1 ennemi par seconde
    #Avant apparition_boss, les ennemis sont des minion, après ce sont des boss
    if(math.floor(prev_time/1000)-math.floor(pygame.time.get_ticks()/1000)!=0):
        r = random.random()
        if(difficulty == 2):
            x = 5
        else : 
            x = 1
        probabilities_ennemi, results_ennemi = getProbabilitiesPoisson(x)
        n = getResult(r, results_ennemi, probabilities_ennemi)
        tab_freq_app.append(n)
        for i in range (0,n):
            if(pygame.time.get_ticks() - start >= apparition_boss*1000):
                newBoss()
            else: 
                newEnnemi()

    prev_time = pygame.time.get_ticks()

    #Mise à jour
    if(pause == False):
        all_sprites.update()
    if(pause == True):
        pygame.time.delay(5000)
        
    #collision des astéroides avec le laser   
    hits = pygame.sprite.groupcollide(Ennemis, bullets, False, True)
    #vérifie si il y a une collision
    for hit in hits:
        score += 50 - hit.radius
        #ajoute un effet sonore pour l'explosion
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        #envoi de bonus de manière aléatoire
        #Fonction random.random () choisit un décimal entre 0 et 1 et envoi un bonus si le nombre est supérieur à 0.9
        if random.random() > 0.9:
            powerup = Bonus(hit.rect.center)
            all_sprites.add(powerup)
            powerups.add(powerup)
        #appelle la fonction new ennemi pour lancer d'autres météorites
        # newEnnemi()
        #AJOUTE
        #ennemi touché perd de la vie ou disparaît
        if(hit.health - hits[hit][0].attack <= 0):
            hit.health = 0
            player.money += 10
            Ennemis.remove(hit)
            all_sprites.remove(hit)
        else:
            hit.health -= hits[hit][0].attack
            
        text = Text(str(-hits[hit][0].attack), 18, (191, 35, 21), 20, 20)
        text.rect.x = hit.rect.x
        text.rect.y = hit.rect.y
        text.time = pygame.time.get_ticks()
        bullets_damages.add(text)
        all_sprites.add(text) 

    #collision des astéroides et du player
    hits = pygame.sprite.spritecollide(player, Ennemis, True, pygame.sprite.collide_circle)
    #vérifie s'il y a une collision
    for hit in hits:
        player.shield -= ennemi.attack
        expl = Explosion(hit.rect.center, 'sm')
        afficheAlea(player, message)
        all_sprites.add(expl)
        message.time = pygame.time.get_ticks()
        all_sprites.add(message)
        # newEnnemi()
        #si la valeur du bouclier atteint 0, le joueur perd une vie et explose
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player_explosion_sound.play()
            show_stats = True
            game_over = True
            
    # vérifie si le joueur heurte un bonus
    hits = pygame.sprite.spritecollide(player, powerups, True)
    #vérifie s'il y a une collision
    for hit in hits:
        #augmente la puissance du tir si le bonus est de type tir
        if hit.type == 'gun':
            player.powerup()
            gun_sound.play()

# Dessin / rendu
    #définition du fond de la fenêtre
    screen.fill(BLACK)
    screen.blit(background, background_rect)

    all_sprites.draw(screen)
    for ennemi in Ennemis.sprites():
        ennemi.draw_bar()

    for damage in bullets_damages.sprites():
        if(prev_time > damage.time + 500):
            all_sprites.remove(damage)
            bullets_damages.remove(damage)
        
    pygame.draw.rect(screen, TURQUOISE, pygame.Rect(0, HEIGHT, WIDTH, INFO_H))
    draw_text(screen, "SCORE : " + str(score), 18, BLACK, WIDTH / 2, 10)

    draw_text(screen, "Temps restant : " + convertMsecToMinSec(duration_game*1000-pygame.time.get_ticks() + start), 18, BLACK, WIDTH/2, 30)
    draw_text(screen, "(3 pour améliorer)", 14, BLACK, WIDTH/2, 50)
    # Affiche la durée de l'apparition des superaléas
    time_boss = apparition_boss*1000 - pygame.time.get_ticks() + start
    if(time_boss >= 0):
        draw_text(screen, "Temps avant apparition des superaléas : " + convertMsecToMinSec(time_boss), 18, BLACK, WIDTH/2, 70)
    # Affiche l'argent du joueur
    lower_attack = player.strength-player.interval
    if(lower_attack<=0):
        lower_attack = 0
    h1 = HEIGHT + 20
    draw_text(screen, "Argent : " + str(player.money), 18, WHITE, 420, h1)
    draw_text(screen, "Points de vie : " + str(player.shield), 18, WHITE, 70, h1)
    draw_shield_bar(screen, 12, h1 + 25, player.shield, 100)
    draw_text(screen, "Précision : " + str(player.accuracy), 18, WHITE, 205, h1)
    draw_text(screen, "Attaque : [" + str(lower_attack) + ", " + str(player.strength+player.interval) + "]", 18, WHITE, 320, h1)
    
    if(prev_time > message.time+1000):
        all_sprites.remove(message)
    else:
        draw_text(screen, message.text, 18, BLACK, message.rect.x+message.rect.width/2, message.rect.y-10+message.rect.height/2)

    # mise à jour de l'affichage
    pygame.display.flip()

pygame.quit()