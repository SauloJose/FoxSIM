import pygame
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arrastar e Rotacionar Retângulo")

# Cores
RECT_COLOR = (0, 128, 255)
HIGHLIGHT_COLOR = (100, 180, 255)
BG_COLOR = (30, 30, 30)

# Retângulo como superfície
rect_size = (150, 100)
base_surface = pygame.Surface(rect_size, pygame.SRCALPHA)
base_surface.fill(RECT_COLOR)

# Estado do retângulo
rect_pos = pygame.Vector2(300, 200)
angle = 0
dragging = False
offset = pygame.Vector2(0, 0)

clock = pygame.time.Clock()

while True:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.Vector2(event.pos)

            # Gira com botão direito SOMENTE se estiver selecionado
            if event.button == 3 and dragging:
                angle += 15
                angle %= 360

            # Seleciona com botão esquerdo
            elif event.button == 1:
                # Gira o retângulo para colisão precisa
                test_surface = pygame.transform.rotate(base_surface, angle)
                test_rect = test_surface.get_rect(center=rect_pos)

                if test_rect.collidepoint(event.pos):
                    dragging = True
                    offset = rect_pos - mouse_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            rect_pos = pygame.Vector2(event.pos) + offset

    # Atualiza cor conforme estado
    current_color = HIGHLIGHT_COLOR if dragging else RECT_COLOR
    base_surface.fill(current_color)

    # Gira e desenha
    rotated_surface = pygame.transform.rotate(base_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=rect_pos)
    screen.blit(rotated_surface, rotated_rect.topleft)

    pygame.display.flip()
    clock.tick(60)
