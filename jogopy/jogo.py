# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random
import time

pygame.init()
pygame.mixer.init()

# ----- Gera tela principal
WIDTH = 800
HEIGHT = 480
window = pygame.display.set_mode((WIDTH, HEIGHT + 100))
pygame.display.set_caption('Navinha')
TILE_SIZE = 40 
# Define a aceleração da gravidade
GRAVITY = 6
# Define a velocidade inicial no pulo
JUMP_SIZE = 250

JUMP_COOLDOWN = 0.5   # Tempo mínimo em segundos entre os pulos

# ----- Inicia assets
zumbi_WIDTH = 50
zumbi_HEIGHT = 38
SHIP_WIDTH = 70
SHIP_HEIGHT = 50
municao_WIDTH = 30
municao_HEIGHT = 40
carro_WIDTH = 100
carro_HEIGHT = 60
onibus_WIDTH = 150
onibus_HEIGHT = 60
assets = {}
assets['background'] = pygame.image.load('jogopy/assets/img/starfield.png').convert()
assets['zumbi1_img'] = pygame.image.load('jogopy/assets/img/zumbi1.png').convert_alpha()
assets['zumbi1_img'] = pygame.transform.scale(assets['zumbi1_img'], (zumbi_WIDTH, zumbi_HEIGHT))
assets['zumbi2_img'] = pygame.image.load('jogopy/assets/img/zumbi2.png').convert_alpha()
assets['zumbi2_img'] = pygame.transform.scale(assets['zumbi2_img'], (zumbi_WIDTH, zumbi_HEIGHT))
assets['ship_img'] = pygame.image.load('jogopy/assets/img/boneco.png').convert_alpha()
assets['ship_img'] = pygame.transform.scale(assets['ship_img'], (SHIP_WIDTH, SHIP_HEIGHT))
assets['bullet_img'] = pygame.image.load('jogopy/assets/img/laserRed16.png').convert_alpha()
assets["municao_img"] = pygame.image.load('jogopy/assets/img/municao.png').convert_alpha()
assets['municao_img'] = pygame.transform.scale(assets['municao_img'], (municao_WIDTH, municao_HEIGHT))
assets['carro_img'] = pygame.image.load('jogopy/assets/img/carro.png').convert_alpha()
assets['carro_img'] = pygame.transform.scale(assets['carro_img'], (carro_WIDTH, carro_HEIGHT))
assets['onibus_img'] = pygame.image.load('jogopy/assets/img/onibus.png').convert_alpha()
assets['onibus_img'] = pygame.transform.scale(assets['onibus_img'], (onibus_WIDTH, onibus_HEIGHT))
explosion_anim = []
for i in range(9):
    # Os arquivos de animação são numerados de 00 a 08
    filename = 'jogopy/assets/img/regularExplosion0{}.png'.format(i)
    img = pygame.image.load(filename).convert()
    img = pygame.transform.scale(img, (32, 32))
    explosion_anim.append(img)
assets["explosion_anim"] = explosion_anim
assets["score_font"] = pygame.font.Font('jogopy/assets/font/PressStart2P.ttf', 28)

# Carrega os sons do jogo
pygame.mixer.music.load('jogopy/assets/snd/tgfcoder-FrozenJam-SeamlessLoop.ogg')
pygame.mixer.music.set_volume(0.4)
assets['boom_sound'] = pygame.mixer.Sound('jogopy/assets/snd/expl3.wav')
assets['destroy_sound'] = pygame.mixer.Sound('jogopy/assets/snd/dano.mp3')
assets['pew_sound'] = pygame.mixer.Sound('jogopy/assets/snd/tiro.mp3')

STILL = 0
JUMPING = 1
FALLING = 2
# ----- Inicia estruturas de dados
# Definindo os novos tipos
class Ship(pygame.sprite.Sprite):
    def __init__(self, groups, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.image = assets['ship_img']
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT/2
        self.rect.bottom = HEIGHT - 150
        self.speedy = 0
        self.groups = groups
        self.assets = assets
        self.last_jump_time = 0.0

        # Só será possível atirar uma vez a cada 500 milissegundos
        self.last_shot = pygame.time.get_ticks()
        self.shoot_ticks = 250

    def update(self):
        # Atualização da posição da nave
        self.speedy += GRAVITY
        # Atualiza o estado para caindo
        if self.speedy > 0:
            self.state = FALLING
        # Atualiza a posição y
        self.rect.y += self.speedy
        # Estava indo para baixo
        if self.speedy > 0:
            # Se colidiu com algo, para de cair
            self.speedy = 0
            # Atualiza o estado para parado
            self.state = STILL
        # Estava indo para cima
        elif self.speedy < 0:
            # Se colidiu com algo, para de cair
            self.speedy = 0
            # Atualiza o estado para parado
            self.state = STILL
        # Mantem dentro da tela
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        # Verifica se pode atirar
        now = pygame.time.get_ticks()
        # Verifica quantos ticks se passaram desde o último tiro.
        elapsed_ticks = now - self.last_shot

        # Se já pode atirar novamente...
        if elapsed_ticks > self.shoot_ticks:
            # Marca o tick da nova imagem.
            self.last_shot = now
            # A nova bala vai ser criada logo acima e no centro horizontal da nave
            new_bullet = Bullet(self.assets, self.rect.bottom - 20, self.rect.centery)
            self.groups['all_sprites'].add(new_bullet)
            self.groups['all_bullets'].add(new_bullet)
            self.assets['pew_sound'].play()
    
    def jump(self):
        current_time = time.time()
        if current_time - self.last_jump_time > JUMP_COOLDOWN:
            self.last_jump_time = current_time
        # Só pode pular se ainda não estiver pulando ou caindo
            if self.state == STILL:
                self.speedy -= JUMP_SIZE
                self.state = JUMPING
                

class Meteor(pygame.sprite.Sprite):
    active_zombies = 0  # Variável para controlar o número de zumbis ativos

    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        zumbi_images = [assets['zumbi1_img'], assets['zumbi2_img']]
        self.image = random.choice(zumbi_images)
        self.rect = self.image.get_rect()
        self.rect.y =   HEIGHT - 50
        self.rect.x = WIDTH  # Posição fixa no eixo x para os zumbis
        self.speedx = random.randint(-9, -2)
        self.spawn_interval = random.uniform(1.0, 3.0)  # Intervalo de tempo entre cada criação
        self.spawn_timer = 0.0

        Meteor.active_zombies += 1  # Incrementa o número de zumbis ativos

    def update(self):
        self.rect.x += self.speedx

        if self.rect.right < 0:
            self.rect.y = HEIGHT - 50
            self.rect.x = WIDTH  # Reinicia a posição do zumbi no eixo x
            self.speedx = random.randint(-9, -2)

        self.spawn_timer += 5.0 / FPS

        if self.spawn_timer >= self.spawn_interval and Meteor.active_zombies == 0:
            self.spawn_timer = 0.0
            self.rect.y = HEIGHT - 50
            Meteor.active_zombies += 1  # Incrementa o número de zumbis ativos

    def kill(self):
        pygame.sprite.Sprite.kill(self)  # Remove o zumbi do grupo de sprites
        Meteor.active_zombies -= 1  # Decrementa o número de zumbis ativos
class Municao(pygame.sprite.Sprite):
    active_municao = 0  # Variável para controlar o número de municao ativos

    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        municao_images = [assets['municao_img'], assets['municao_img']]
        self.image = random.choice(municao_images)
        self.rect = self.image.get_rect()
        self.rect.y =   HEIGHT - 100
        self.rect.x = WIDTH  # Posição fixa no eixo x para os zumbis
        self.speedx = -3
        self.spawn_interval = random.uniform(10, 20)  # Intervalo de tempo entre cada criação
        self.spawn_timer = 0.0

        Municao.active_municao += 1  # Incrementa o número de zumbis ativos

    def update(self):
        self.rect.x += self.speedx

        if self.rect.right < 0:
            self.rect.y = HEIGHT - 100
            self.rect.x = WIDTH  # Reinicia a posição do zumbi no eixo x
            self.speedx = -3
            self.speedx = random.randint(-9, -2)

        #self.spawn_timer += 5.0 / FPS

        # if self.spawn_timer >= self.spawn_interval and Meteor.active_zombies == 0:
        #     self.spawn_timer = 0.0
        #     self.rect.y = HEIGHT - 50
        #     Meteor.active_zombies += 1  # Incrementa o número de zumbis ativos

    def kill(self):
        pygame.sprite.Sprite.kill(self)  # Remove o zumbi do grupo de sprites
        Meteor.active_zombies -= 1  # Decrementa o número de zumbis ativos

class carro(pygame.sprite.Sprite):
    active_carro = 0  # Variável para controlar o número de zumbis ativos

    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        #zumbi_images = [assets['zumbi1_img'], assets['zumbi2_img']]
        self.image = assets['carro_img']
        self.rect = self.image.get_rect()
        self.rect.y =   HEIGHT - 60
        self.rect.x = WIDTH  # Posição fixa no eixo x para os zumbis
        self.speedx = random.randint(-12, -9)
        self.spawn_interval = random.uniform(1.0, 3.0)  # Intervalo de tempo entre cada criação
        self.spawn_timer = 0.0

        carro.active_carro += 1  # Incrementa o número de zumbis ativos

    def update(self):
        self.rect.x += self.speedx

        if self.rect.right < 0:
            self.rect.y = HEIGHT - 60
            self.rect.x = WIDTH  # Reinicia a posição do zumbi no eixo x
            self.speedx = random.randint(-16, -9)

        self.spawn_timer += 5.0 / FPS

        if self.spawn_timer >= self.spawn_interval and carro.active_carro == 0:
            self.spawn_timer = 0.0
            self.rect.y = HEIGHT - 50
            carro.active_carro += 1  # Incrementa o número de zumbis ativos

    def kill(self):
        carro.active_carro -= 1  # Decrementa o número de zumbis ativos



# Classe Bullet que representa os tiros
class Bullet(pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, assets, bottom, centery):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.image = assets['bullet_img']
        self.rect = self.image.get_rect()

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.centery = centery
        self.rect.bottom = bottom
        self.speedx = 10  # Velocidade fixa para cima

    def update(self):
        # A bala só se move no eixo x
        self.rect.x += self.speedx

        # Se o tiro passar do inicio da tela, morre.
        if self.rect.bottom > WIDTH:
            self.kill()

# Classe que representa uma explosão de meteoro
class Explosion(pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, center, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        # Armazena a animação de explosão
        self.explosion_anim = assets['explosion_anim']

        # Inicia o processo de animação colocando a primeira imagem na tela.
        self.frame = 0  # Armazena o índice atual na animação
        self.image = self.explosion_anim[self.frame]  # Pega a primeira imagem
        self.rect = self.image.get_rect()
        self.rect.center = center  # Posiciona o centro da imagem

        # Guarda o tick da primeira imagem, ou seja, o momento em que a imagem foi mostrada
        self.last_update = pygame.time.get_ticks()

        # Controle de ticks de animação: troca de imagem a cada self.frame_ticks milissegundos.
        # Quando pygame.time.get_ticks() - self.last_update > self.frame_ticks a
        # próxima imagem da animação será mostrada
        self.frame_ticks = 50

    def update(self):
        # Verifica o tick atual.
        now = pygame.time.get_ticks()
        # Verifica quantos ticks se passaram desde a ultima mudança de frame.
        elapsed_ticks = now - self.last_update

        # Se já está na hora de mudar de imagem...
        if elapsed_ticks > self.frame_ticks:
            # Marca o tick da nova imagem.
            self.last_update = now

            # Avança um quadro.
            self.frame += 1

            # Verifica se já chegou no final da animação.
            if self.frame == len(self.explosion_anim):
                # Se sim, tchau explosão!
                self.kill()
            else:
                # Se ainda não chegou ao fim da explosão, troca de imagem.
                center = self.rect.center
                self.image = self.explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Variável para o ajuste de velocidade
clock = pygame.time.Clock()
FPS = 30

# Criando um grupo de meteoros
all_sprites = pygame.sprite.Group()
all_meteors = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()
all_carros = pygame.sprite.Group()
all_municao = pygame.sprite.Group()

groups = {}
groups['all_sprites'] = all_sprites
groups['all_meteors'] = all_meteors
groups['all_bullets'] = all_bullets
groups["all_municao"] = all_municao
groups['all_carros'] = all_carros

# Criando o jogador
player = Ship(groups, assets)
all_sprites.add(player)
x = 8
# Criando os meteoros
for i in range(1):
    municao = Municao(assets)
    all_sprites.add(municao)
    all_municao.add(municao)

for i in range(x):
    meteor = Meteor(assets)
    all_sprites.add(meteor)
    all_meteors.add(meteor)
y = 1
for i in range(y):
    carro1 = carro(assets)
    all_sprites.add(carro1)
    all_carros.add(carro1)

DONE = 0
PLAYING = 1
EXPLODING = 2
state = PLAYING

keys_down = {}
score = 0
lives = 3
contadorvidas = 0
municao = 20

# ===== Loop principal =====
pygame.mixer.music.play(loops=-1)
while state != DONE:
    clock.tick(FPS)

    # ----- Trata eventos
    for event in pygame.event.get():
        # ----- Verifica consequências
        if event.type == pygame.QUIT:
            state = DONE
        # Só verifica o teclado se está no estado de jogo
        if state == PLAYING:
            # Verifica se apertou alguma tecla.
            if event.type == pygame.KEYDOWN:
                # Dependendo da tecla, altera a velocidade.
                keys_down[event.key] = True
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_SPACE:
                    player.shoot()
            # Verifica se soltou alguma tecla.
            if event.type == pygame.KEYUP:
                # Dependendo da tecla, altera a velocidade.
                if event.key in keys_down and keys_down[event.key]:
                    if event.key == pygame.K_UP:
                        player.speedy += 8
                    if event.key == pygame.K_DOWN:
                        player.speedy -= 8


    # ----- Atualiza estado do jogo
    # Atualizando a posição dos meteoros
    all_sprites.update()

    if state == PLAYING:
        # Verifica se houve colisão entre tiro e meteoro
        hits = pygame.sprite.groupcollide(all_meteors, all_bullets, True, True)
        for meteor in hits: # As chaves são os elementos do primeiro grupo (meteoros) que colidiram com alguma bala
            # O meteoro e destruido e precisa ser recriado
            assets['destroy_sound'].play()
            m = Meteor(assets)
            all_sprites.add(m)
            all_meteors.add(m)

            # No lugar do meteoro antigo, adicionar uma explosão.
            explosao = Explosion(meteor.rect.center, assets)
            all_sprites.add(explosao)

       

            # Ganhou pontos!
            score += 20
            contadorvidas += 20
            if contadorvidas == 400:
                contadorvidas = 0
                lives += 1

        # Verifica se houve colisão entre nave e meteoro

        hits2 = pygame.sprite.spritecollide(player, all_municao, True)

        if hits2:
            municao += 5
        

        hits = pygame.sprite.spritecollide(player, all_meteors, True)
        if len(hits) > 0:
            # Toca o som da colisão
            assets['boom_sound'].play()
            player.kill()
            lives -= 1
            explosao = Explosion(player.rect.center, assets)
            all_sprites.add(explosao)
            state = EXPLODING
            keys_down = {}
            explosion_tick = pygame.time.get_ticks()
            explosion_duration = explosao.frame_ticks * len(explosao.explosion_anim) + 400
        hits = pygame.sprite.spritecollide(player, all_carros, True)
        if len(hits) > 0:
            # Toca o som da colisão
            assets['boom_sound'].play()
            player.kill()
            lives -= 1
            explosao = Explosion(player.rect.center, assets)
            all_sprites.add(explosao)
            state = EXPLODING
            keys_down = {}
            explosion_tick = pygame.time.get_ticks()
            explosion_duration = explosao.frame_ticks * len(explosao.explosion_anim) + 400
    elif state == EXPLODING:
        now = pygame.time.get_ticks()
        if now - explosion_tick > explosion_duration:
            if lives == 0:
                state = DONE
            else:
                state = PLAYING
                player = Ship(groups, assets)
                all_sprites.add(player)

    # ----- Gera saídas
    window.fill((0, 0, 0))  # Preenche com a cor branca
    window.blit(assets['background'], (0, 0))
    # Desenhando meteoros
    all_sprites.draw(window)

    # Desenhando o score
    text_surface = assets['score_font'].render("Pontos: {:08d}".format(score), True, (255, 255, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (WIDTH / 2,  10)
    window.blit(text_surface, text_rect)
    # Desenhando o score

    text_surface = assets['score_font'].render("Municao: {:08d}".format(municao), True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (WIDTH / 2,  40)
    window.blit(text_surface, text_rect)


    # Desenhando as vidas
    text_surface = assets['score_font'].render(chr(9829) * lives, True, (255, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.bottomleft = (WIDTH - 100, HEIGHT - 10)
    window.blit(text_surface, text_rect)

    pygame.display.update()  # Mostra o novo frame para o jogador

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

