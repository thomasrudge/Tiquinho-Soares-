import pygame
import imageio

def reproduzir_animacao(caminho_gif, largura, altura, taxa_atualizacao):
    # Inicialize o Pygame
    pygame.init()

    # Carregue o GIF animado
    gif = imageio.mimread(caminho_gif)
    num_quadros = len(gif)

    # Defina a largura e a altura da tela
    tela = pygame.display.set_mode((largura, altura))

    # Defina o índice inicial do quadro
    indice_quadro = 0

    # Crie um relógio para controlar a taxa de atualização
    relogio = pygame.time.Clock()

    # Loop principal do jogo
    terminado = False
    while not terminado:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                terminado = True

        # Limpe a tela
        tela.fill((0, 0, 0))

        # Exiba o quadro atual na tela
        quadro = pygame.surfarray.make_surface(gif[indice_quadro])
        tela.blit(quadro, (0, 0))

        # Atualize a tela
        pygame.display.flip()

        # Atualize o índice do quadro
        indice_quadro = (indice_quadro + 1) % num_quadros

        # Aguarde a taxa de atualização
        relogio.tick(taxa_atualizacao)

    # Encerre o Pygame
    pygame.quit()

# Exemplo de uso da função
reproduzir_animacao("caminho/do/final.gif", 800, 600, 30)
