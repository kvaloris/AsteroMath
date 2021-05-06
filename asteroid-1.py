# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
import pygame
import random
import os


WIDTH = 480
HEIGHT = 600
FPS = 60

# définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# initialisation de pygame et création de la fenêtre
pygame.init()
pygame.mixer.init()
#définition de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
#nom de la fenêtre
pygame.display.set_caption("asteroid")
clock = pygame.time.Clock()
POWERUP_TIME = 5000


# mise en place des ressources
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'Images')
# chargement des graphiques pour le jeu
background = pygame.image.load(os.path.join(img_folder, "galaxy3.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_folder, 'vaisseau11.png')).convert()
bullet_img = pygame.image.load(os.path.join(img_folder, 'laser.png')).convert()
player_img = pygame.image.load(os.path.join(img_folder, "vaisseau11.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
#création d'une liste comportant diverses images de météorites
meteor_images = []
meteor_list = ['meteor.png', 'meteor2.png', 'meteor6.png', 'meteor7.png', 'meteor5.png', 'meteor8.png', 'meteor9.png', 'meteor10.png', 'meteor11.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, img)).convert_alpha()) 
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
powerup_images['shield'] = pygame.image.load(os.path.join(img_folder, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(os.path.join(img_folder, 'bolt_gold.png')).convert()

# Chargement de tous les musiques et effets sonores
snd_dir = os.path.join(game_folder, 'snd')
shield_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'shield.wav'))
gun_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'gun.wav'))
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pew.wav'))
player_explosion_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'explosion.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_dir, snd)))
pygame.mixer.music.load(os.path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.mp3'))
pygame.mixer.music.set_volume(0.4)

#définition d'une nouvelle météorite
def newEnnemi():
    m = Ennemi()
    all_sprites.add(m)
    Ennemis.add(m) 

#définition d'une barre de progression de la qualité du bouclier
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

#définition des vies du joueur avec les images du vaisseau    
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)
        
#définition d'unécran explicatif
def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "IT'S A TRAP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Flèches pour se déplacer, Espace pour tirer", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Appuyez sur une touche pour commencer", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
        
#création d'un sprite avec le vaisseau
class Player(pygame.sprite.Sprite):
    def __init__(self):
        #self est une convention de python pour le premier paramètre d'une instance
        pygame.sprite.Sprite.__init__(self)
         
        #définition de la taille du rectangle
        self.image = pygame.Surface((50, 40))
        #couleur de l'élément
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        #définition du rayon de la surface du joueur
        self.radius = 32
        #définition de la position du rectangle (vaisseau)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        #définition de la vitesse
        self.speedx = 0
        #définition de la valeur du bouclier
        self.shield = 100
        #mise en place d'une image pour le joueur
        self.image= player_img
        self.image.set_colorkey(BLACK)
        self.shoot_delay = 250
        self.lives = 3
        self.hidden = False
        self.last_shot = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

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

    #définition de la fonction permettant de tirer    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            #production d'une météorite si le bonus = 1
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            #production de deux météorites si le bonus est > 1
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
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

        
#création d'un sprite pour l'astéroïde          
class Ennemi(pygame.sprite.Sprite):
    def __init__(self):
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
        self.image_orig = random.choice(meteor_images)
        self.image.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
    
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
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
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

#création de groupes pour lancer les éléments dans la fenêtre
all_sprites = pygame.sprite.Group()
powerups = pygame.sprite.Group()
Ennemis= pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
#ennemi = Ennemi()
#all_sprites.add(ennemi)
for i in range (8):
    newEnnemi()



score=0
#Met la musique de fond en boucle
pygame.mixer.music.play(loops=-1)

#appel d'une police et mise en place de celle-ci
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

   
# Boucle du jeu
game_over = True
running = True
while running:
    #si le joueur a perdu et souhaite rejouer, les éléments sont recréés
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newEnnemi()
        score = 0
    #continue de jouer la boucle à la bonne vitesse
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # vérifie si la fenêtre se ferme
        if event.type == pygame.QUIT:
            running = False
    


    #Mise à jour
    all_sprites.update()
    
        
    #collision des astéroides avec le laser   
    hits = pygame.sprite.groupcollide(Ennemis, bullets, True, True)
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
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        #appelle la fonction new ennemi pour lancer d'autres météorites
        newEnnemi()
        
        
    #collision des astéroides et du vaisseau
    hits = pygame.sprite.spritecollide(player, Ennemis, True, pygame.sprite.collide_circle)
    #vérifie s'il y a une collision
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newEnnemi()
        #si la valeur du bouclier atteint 0, le joueur perd une vie et explose
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
            player_explosion_sound.play()
        # si le joueur meurt et les explosions finissent
        if player.lives == 0 and not death_explosion.alive():
            #permet de lancer la condition du game over
            game_over = True
            
    # vérifie si le joueur heurte un bonus
    hits = pygame.sprite.spritecollide(player, powerups, True)
    #vérifie s'il y a une collision
    for hit in hits:
        #augmente le bouclier si le bonus est de type bouclier
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
            shield_sound.play()
        #augmente la puissance du tir si le bonus est de type tir
        if hit.type == 'gun':
            player.powerup()
            gun_sound.play()
    
# Dessin / rendu
    #définition du fond de la fenêtre
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    # mise à jour de l'affichage
    pygame.display.flip()

pygame.quit()
