import pygame

pygame.init()

# VENTANA

ANCHO = 900
ALTO = 500
FPS = 60

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Supervivientes vs Zombies")

reloj = pygame.time.Clock()

# FUENTES

fuente = pygame.font.SysFont("Arial", 18)
fuenteGrande = pygame.font.SysFont("Arial", 40)

# CARRILES

CARRILES = [130, 250, 370]

# COLORES

BLANCO = (255, 255, 255)
NEGRO = (30, 30, 30)

ROJO = (230, 60, 60)
VERDE = (50, 200, 80)
AZUL = (60, 120, 230)

AMARILLO = (240, 220, 50)
NARANJA = (255, 150, 50)
MORADO = (180, 80, 220)
CIAN = (60, 210, 220)