
# ----- Importa e inicia pacotes
import pygame
import random
import time
import shelve

# Inicialização do Pygame
pygame.init()

def adicionar_pontuacao(nome, pontuacao):
    with shelve.open('pontuacoes.db') as db:
        if nome in db:
            # Se o jogador já existe, atualiza a pontuação se for maior
            if pontuacao > db[nome]:
                db[nome] = pontuacao
        else:
            # Se o jogador não existe, adiciona a pontuação
            db[nome] = pontuacao


# Configurações da janel
largura = 800
altura = 480
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Nome do Jogador")

# Configurações da entrada de texto
fonte = pygame.font.Font(None, 32)
nome = ''
cor_fundo = (255, 255, 255)
cor_texto = (0, 0, 0)

# Carrega a imagem de fundo
imagem_fundo = pygame.image.load("jogopy/assets/img/telainicial.png")
imagem_fundo = pygame.transform.scale(imagem_fundo, (largura, altura))

# Loop principal
rodando = True
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                rodando = False
            elif event.key == pygame.K_BACKSPACE:
                nome = nome[:-1]
            else:
                nome += event.unicode

    # Desenha a imagem de fundo na tela
    tela.blit(imagem_fundo, (0, 0))

    # Desenha o retângulo de entrada de texto
    #pygame.draw.rect(tela, cor_texto, (200, 200, 400, 50), 2)

    # Renderiza o texto digitado
    texto_renderizado = fonte.render(nome, True, cor_texto)
    tela.blit(texto_renderizado, (330, 230))

    pygame.display.flip()

# ----- Gera tela principal
WIDTH = 800
HEIGHT = 480
window = pygame.display.set_mode((WIDTH, HEIGHT + 100))
pygame.display.set_caption('sobreviventes do python')
TILE_SIZE = 40 
# Define a aceleração da gravidade
GRAVITY = 3.5 
# Define a velocidade inicial no pulo
JUMP_SIZE = 170

JUMP_COOLDOWN = 0.5    # Tempo mínimo em segundos entre os pulos

# ----- Inicia assets
zumbi_WIDTH = 70
zumbi_HEIGHT = 58
SHIP_WIDTH = 110
SHIP_HEIGHT = 90
municao_WIDTH = 30
municao_HEIGHT = 40
carro_WIDTH = 100
carro_HEIGHT = 60
onibus_WIDTH = 150
onibus_HEIGHT = 60
assets = {}
assets['final'] = pygame.image.load('jogopy/assets/img/final.gif').convert_alpha()
assets['final'] = pygame.transform.scale(assets['final'], (zumbi_WIDTH + 200, zumbi_HEIGHT + 200))
assets['bola'] = pygame.image.load('jogopy/assets/img/bola.png').convert_alpha()
assets['bola'] = pygame.transform.scale(assets['bola'], (zumbi_WIDTH + 30, zumbi_HEIGHT + 30))
assets['tela'] = pygame.image.load('jogopy/assets/img/telainicial.png').convert_alpha()
assets['background'] = pygame.image.load('jogopy/assets/img/fundo1.jpg').convert_alpha()
assets['background'] = pygame.transform.scale(assets['background'], (WIDTH, HEIGHT + 50))
assets['zumbi1_img'] = pygame.image.load('jogopy/assets/img/zumbi1.png').convert_alpha()
assets['zumbi1_img'] = pygame.transform.scale(assets['zumbi1_img'], (zumbi_WIDTH + 10, zumbi_HEIGHT + 10))
assets['zumbi2_img'] = pygame.image.load('jogopy/assets/img/zumbi2.png').convert_alpha()
assets['zumbi2_img'] = pygame.transform.scale(assets['zumbi2_img'], (zumbi_WIDTH + 20, zumbi_HEIGHT + 20))
assets['ship_img'] = pygame.image.load('jogopy/assets/img/boneco2.png').convert_alpha()
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
        self.rect.centerx = 80
        self.rect.bottom = HEIGHT
        self.speedy = 0
        self.groups = groups
        self.assets = assets
        self.last_jump_time = 0.0

        # Só será possível atirar uma vez a cada 500 milissegundos
        self.last_shot = pygame.time.get_ticks()
        self.shoot_ticks = 0

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
    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        zumbi_images = [assets['zumbi1_img'], assets['zumbi2_img']]
        self.image = random.choice(zumbi_images)
        self.rect = self.image.get_rect()
        self.rect.y = HEIGHT - 80
        self.rect.x = WIDTH  # Posição fixa no eixo x para os zumbis
        self.speedx = random.randint(-9, -2)

    def update(self):
        self.rect.x += self.speedx

        if self.rect.right < 0:
            self.rect.y = HEIGHT - 80
            self.rect.x = WIDTH  # Reinicia a posição do zumbi no eixo x
            self.speedx = random.randint(-9, -2)


class final(pygame.sprite.Sprite):
    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets['final']
        self.rect = self.image.get_rect()
        self.rect.y = HEIGHT - 250
        self.rect.x = WIDTH - 250
        self.speedy = 0
        self.groups = groups
        self.assets = assets
        self.last_shot = pygame.time.get_ticks()
        self.shoot_ticks = 500

    def update(self):
        self.rect.y += self.speedy
        if self.rect.y < 100 or self.rect.y > 300:
            self.rect.y = HEIGHT - 250
            self.rect.centerx = WIDTH // 2
            self.speedy = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        elapsed_ticks = now - self.last_shot

        if elapsed_ticks > self.shoot_ticks:
            self.last_shot = now
            # Ajuste a posição de partida da bola em relação ao objeto final
            bola_start_x = self.rect.centerx
            bola_start_y = self.rect.y
            new_Bola = Bola(self.assets, bola_start_x, bola_start_y, player.speedy)
            self.groups['all_sprites'].add(new_Bola)
            self.groups['all_bola'].add(new_Bola)
            self.assets['pew_sound'].play()


class Bola(pygame.sprite.Sprite):
    def __init__(self, assets, start_x, start_y, player_speedy):
        pygame.sprite.Sprite.__init__(self)

        self.image = assets['bola']
        self.rect = self.image.get_rect()
        self.rect.centerx = start_x
        self.rect.bottom = start_y+ 100 # Definir a posição inicial da bola em relação ao objeto final
        self.speedx = -13
        self.speedy = random.randint(-5, 5)  # Velocidade vertical da bola igual à velocidade do jogador

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.x < 0:
            self.kill()



class Municao(pygame.sprite.Sprite):
    active_municao = 0  # Variável para controlar o número de municao ativos

    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets['municao_img']
        self.rect = self.image.get_rect()
        self.rect.y =   HEIGHT - 150
        self.rect.x = WIDTH  # Posição fixa no eixo x para os zumbis
        self.speedx = -6


    def update(self):
        self.rect.x += self.speedx

        if self.rect.right < 0:
            self.rect.y = HEIGHT - 150
            self.rect.x = WIDTH  # Reinicia a posição do zumbi no eixo x
            self.speedx = -6

class carro(pygame.sprite.Sprite):
    active_carros = 0  # Variável para controlar o número de carros ativos
    pontos_para_onibus = 1000  # Pontuação necessária para mudar para a imagem de ônibus
    imagem_carro = assets['carro_img']
    imagem_onibus = assets['onibus_img']

    def __init__(self, assets):
        pygame.sprite.Sprite.__init__(self)
        self.image = carro.imagem_carro
        self.rect = self.image.get_rect()
        self.rect.y = HEIGHT - 60
        self.rect.x = WIDTH  # Posição fixa no eixo x para os carros
        self.speedx = random.randint(-12, -9)
        self.spawn_interval = random.uniform(1.0, 3.0)  # Intervalo de tempo entre cada criação
        self.spawn_timer = 0.0

        carro.active_carros += 1  # Incrementa o número de carros ativos

    def update(self):
        self.rect.x += self.speedx
        if score < 2000:

            if self.rect.right < 0:
                self.rect.y = HEIGHT - 60
                self.rect.x = WIDTH  # Reinicia a posição do carro no eixo x
                self.speedx = random.randint(-16, -9)

            self.spawn_timer += 5.0 / FPS

            if score > carro.pontos_para_onibus and self.image == carro.imagem_carro:
                extra = 1
                for _ in range(extra):
                    self.image = carro.imagem_onibus

            if self.spawn_timer >= self.spawn_interval and carro.active_carros == 0:
                self.spawn_timer = 0.0
                self.rect.y = HEIGHT - 50
                carro.active_carros += 1  # Incrementa o número de carros ativos

    def kill(self):
        carro.active_carros -= 1  # Decrementa o número de carros ativos




# Classe Bullet que representa os tiros
class Bullet(pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, assets, bottom, centery):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.image = assets['bullet_img']
        self.rect = self.image.get_rect()

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.centerx = 130
        self.rect.centery = centery
        self.rect.bottom = bottom - 30
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
rank = []
ejogador = 0
def exibir_pontuacoes():
    with shelve.open('pontuacoes.db') as db:
        # Cria o ranking com base nas pontuações
        ranking = sorted(db.items(), key=lambda item: item[1], reverse=True)
        # Imprime o ranking
        for i, jogador_pontos in enumerate(ranking, start=1):
            jogador, pontos = jogador_pontos
            if jogador == nome:
                rank.append([i,jogador,pontos])
            else:
                rank.append([i,jogador,pontos])
            

def Fgame_over(window):
    # Limpa a tela
    window.fill((0, 0, 0))  # Preenche a tela com a cor preta (pode ser substituída pela cor de fundo desejada)
    imagem_fundo = pygame.image.load("jogopy/assets/img/telafinal.png")
    imagem_fundo = pygame.transform.scale(imagem_fundo, (800, 600))
    # Desenha a imagem de fundo na tela
    tela.blit(imagem_fundo, (0, 0))
    # Exibe a mensagem de "Game Over" no centro da tela
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    window.blit(text, text_rect)

    font = pygame.font.Font(None, 36)
    text = font.render("Seu ranking:", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, (HEIGHT / 2)+100))
    window.blit(text, text_rect)
    for x in rank:
        if x[1] == nome:
            posicao = x[0]
            pontuacao = x[2]
    font = pygame.font.Font(None, 36)
    text = font.render("{0}º{1}".format(posicao,nome), True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, (HEIGHT / 2)+150))
    window.blit(text, text_rect)

    font = pygame.font.Font(None, 36)
    text = font.render("Seu recorde: {0}".format(pontuacao), True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, (HEIGHT / 2)-100))
    window.blit(text, text_rect)

    # Atualiza a tela
    pygame.display.flip()

# Variável para o ajuste de velocidade
clock = pygame.time.Clock()
FPS = 30

# Criando um grupo de meteoros
all_sprites = pygame.sprite.Group()
all_meteors = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()
all_carros = pygame.sprite.Group()
all_municao = pygame.sprite.Group()
all_final = pygame.sprite.Group()
all_bola = pygame.sprite.Group()

groups = {}
groups['all_sprites'] = all_sprites
groups['all_meteors'] = all_meteors
groups['all_bullets'] = all_bullets
groups["all_municao"] = all_municao
groups['all_carros'] = all_carros
groups['all_final'] = all_final
groups['all_bola'] = all_bola

# Criando o jogador
player = Ship(groups, assets)
all_sprites.add(player)
municao1 = Municao(assets)
all_sprites.add(municao1)
all_municao.add(municao1)
# Criando os meteoros
meteor = Meteor(assets)
all_meteors.add(meteor)

carro1 = carro(assets)
all_sprites.add(carro1)
all_carros.add(carro1)

DONE = 0
PLAYING = 1
EXPLODING = 2
game_over = 3
state = PLAYING
quantidade_zumbies = 0
keys_down = {}
score = 0
lives = 2
contadorvidas = 0
quantidade_municao = 20
c = 1
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
                    if c == 2:
                        final1.shoot()
                    quantidade_municao -= 1
            # Verifica se soltou alguma tecla.
            if event.type == pygame.KEYUP:
                # Dependendo da tecla, altera a velocidade.
                if event.key in keys_down and keys_down[event.key]:
                    if event.key == pygame.K_DOWN:
                        player.speedy += 200
            if score > 200 + (quantidade_zumbies * 200):
            # Calcula a quantidade de zumbis extras a serem adicionados
                extra_zombies = (score) // 200 - quantidade_zumbies
                for _ in range(extra_zombies):
                    meteor = Meteor(assets)
                    all_meteors.add(meteor)
                    quantidade_zumbies += 1  # Incrementa a quantidade de zumbis extras adicionados
        if state == game_over:
            if event.type == pygame.QUIT:
                state = DONE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    c = 1
                    all_bola = pygame.sprite.Group()
                    all_final = pygame.sprite.Group()
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
                    groups["all_municao"] = all_municao
                    groups['all_bola'] = all_bola
                    groups['all_final'] = all_final
                    quantidade_zumbies = 0
                    keys_down = {}
                    score = 0
                    lives = 3
                    contadorvidas = 0
                    quantidade_municao = 20
                    player = Ship(groups, assets)
                    all_sprites.add(player)
                    meteor = Meteor(assets)
                    all_meteors.add(meteor)
                    municao1 = Municao(assets)
                    all_sprites.add(municao1)
                    all_municao.add(municao1)
                    carro1 = carro(assets)
                    all_sprites.add(carro1)
                    all_carros.add(carro1)
                    all_sprites.update()
                    all_meteors.update()
                    
                    state = PLAYING

    # ----- Atualiza estado do jogo
    # Atualizando a posição dos meteoros
    if c != 2:
        all_sprites.update()
        all_meteors.update()
    if c == 2:
        all_final.update()
        all_sprites.update()
    if score > 1000 and c == 1:
        all_sprites = pygame.sprite.Group()
        all_meteors = pygame.sprite.Group()
        all_bullets = pygame.sprite.Group()
        all_carros = pygame.sprite.Group()
        all_municao = pygame.sprite.Group()
        groups['all_sprites'] = all_sprites
        groups['all_meteors'] = all_meteors
        groups['all_bullets'] = all_bullets
        groups["all_municao"] = all_municao
        groups['all_carros'] = all_carros
        c = 2
        dano = 0
        lives = 5
        contadorvidas = 0
        xmuni = quantidade_municao
        quantidade_municao = 200
        player = Ship(groups, assets)
        all_sprites.add(player)
        final1 = final(assets)
        all_final.add(final1)
        all_sprites.update()
        all_final.update()

        

    if state != DONE:
        if lives <= 0 or quantidade_municao <= 0:
            adicionar_pontuacao(nome, score)
            exibir_pontuacoes()
            state = game_over
            Fgame_over(window)

    if state == PLAYING:
        hits = pygame.sprite.spritecollide(player, all_bola, True)
        if len(hits) > 0:
            assets['destroy_sound'].play()
            explosao = Explosion(player.rect.center, assets)
            all_sprites.add(explosao)
            lives -= 1
        # Verificar colisões entre os objetos "final1" e "all_bullets"
        hits = pygame.sprite.groupcollide(all_final, all_bullets, False,True)

# Verificar se algum objeto final foi atingido por mais de 5 objetos
        if len(hits) > 0:
            dano += 1
            assets['destroy_sound'].play()
            explosao = Explosion(final1.rect.center, assets)
            all_sprites.add(explosao)
            if dano == 50:
                live = 2
                assets['destroy_sound'].play()
                explosao = Explosion(meteor.rect.center, assets)
                all_sprites.add(explosao)
                all_bola = pygame.sprite.Group()
                all_final = pygame.sprite.Group()
                groups["all_municao"] = all_municao
                groups['all_carros'] = all_carros
                quantidade_municao = xmuni
                c = 3
                carro1 = carro(assets)
                all_sprites.add(carro1)
                all_carros.add(carro1)
                municao1 = Municao(assets)
                all_sprites.add(municao1)
                all_municao.add(municao1)
                for t in range(quantidade_zumbies + 1):
                    mt = Meteor(assets)
                    all_meteors.add(mt)
 
    
        hits = pygame.sprite.groupcollide(all_meteors, all_bullets, True, True)
        for meteor in hits: # As chaves são os elementos do primeiro grupo (meteoros) que colidiram com alguma bala
            # O meteoro e destruido e precisa ser recriado
            assets['destroy_sound'].play()
            m = Meteor(assets)
            #all_sprites.add(m) 
            all_meteors.add(m)

            # No lugar do meteoro antigo, adicionar uma explosão.
            explosao = Explosion(meteor.rect.center, assets)
            all_sprites.add(explosao)

       

            # Ganhou pontos!
            score += 20
            contadorvidas += 20
            if contadorvidas == 600:
                contadorvidas = 0
                if score < 3500:
                    lives += 1

        # Verifica se houve colisão entre nave e meteoro

        hits2 = pygame.sprite.spritecollide(player,all_municao, True)

        if len(hits2) > 0:
            for t in range(len(hits2)):
                mu = Municao(assets)
                all_sprites.add(mu) 
                all_municao.add(mu)
                if score < 1000:
                    quantidade_municao += 5
                if score >= 1000 and score < 1500:
                    quantidade_municao += 15
                if score >= 1500 and score < 2000:
                    quantidade_municao += 20
                if score >= 2000 and score < 3000:
                    quantidade_municao += 25
                if score >= 3000 and score < 5000:
                    quantidade_municao += 40

        
        

        hits = pygame.sprite.spritecollide(player, all_meteors, True)
        if len(hits) > 0:
            # Toca o som da colisão
            assets['boom_sound'].play()
            player.kill()
            all_meteors = pygame.sprite.Group()
            for t in range(quantidade_zumbies + 1):
                mt = Meteor(assets)
                all_meteors.add(mt)
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
            all_meteors = pygame.sprite.Group()
            for t in range(quantidade_zumbies + 1):
                mt = Meteor(assets)
                all_meteors.add(mt)
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
            state = PLAYING
            player = Ship(groups,assets)
            all_sprites.add(player)
            
        

    # ----- Gera saídas
    if state != game_over:
        window.fill((0, 0, 0))  # Preenche com a cor branca
        window.blit(assets['background'], (0, 0))
        # Desenhando meteoros
        all_final.draw(window)
        all_meteors.draw(window)
        all_sprites.draw(window)

        # Desenhando o score
        text_surface = assets['score_font'].render("Pontos: {:08d}".format(score), True, (255, 255, 0))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (WIDTH / 2,  10)
        window.blit(text_surface, text_rect)
        # Desenhando o score

        text_surface = assets['score_font'].render("Municao: {:08d}".format(quantidade_municao), True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (WIDTH / 2,  40)
        window.blit(text_surface, text_rect)


        # Desenhando as vidas
        text_surface = assets['score_font'].render(chr(9829) * lives, True, (255, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = ((WIDTH - 100)/ 2, 120 )
        window.blit(text_surface, text_rect)

        pygame.display.update()  # Mostra o novo frame para o jogador

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados
