import math
import random

import pygame

from config import (
    pantalla,
    ANCHO,
    ALTO,
    CARRILES,
    fuente,
    fuentePequena,
    fuenteEnorme,
    BLANCO,
    ROJO,
    VERDE,
    AZUL,
    AMARILLO,
    NARANJA,
    MORADO,
    CIAN
)


HORIZONTE = 80

PIEL_HUMANA = (232, 190, 150)
PIEL_HERIDA = (245, 120, 110)
PIEL_ZOMBIE = (122, 168, 98)

SANGRE_HUMANA = (200, 30, 30)
SANGRE_ZOMBIE = (110, 190, 60)

ROPA_SUPERVIVIENTES = [
    ((200, 120, 60), (70, 62, 55), (90, 60, 30)),
    ((70, 150, 120), (60, 60, 75), (40, 30, 25)),
    ((170, 70, 90), (55, 70, 60), (200, 170, 90)),
]

ROPA_ZOMBIE = ((95, 88, 78), (55, 58, 90), (45, 55, 38))

ROPA_JUGADOR = ((50, 90, 160), (40, 50, 70), (60, 75, 55))

COLOR_ESTADO_SUPERVIVIENTE = {
    "CAMINAR": VERDE,
    "HUYENDO": AMARILLO,
    "HERIDO": ROJO,
    "A_SALVO": MORADO,
}

COLOR_ESTADO_ZOMBIE = {
    "VAGANDO": ROJO,
    "LLEGANDO": NARANJA,
    "ATACANDO": MORADO,
    "ESPERANDO": AMARILLO,
    "RETROCEDIENDO": CIAN,
}

COLOR_HUMOR = {
    "CALMADO": CIAN,
    "HAMBRIENTO": NARANJA,
    "FURIOSO": ROJO,
}

# Colores para mostrar, de forma separada, la estrategia
# elegida por la capa de teoría de juegos.
COLOR_ESTRATEGIA_JUEGO = {
    "DISPARAR": CIAN,
    "HUIR": AMARILLO,
    "ATACAR": ROJO,
    "ESQUIVAR": CIAN,
}


def tiempo():

    return pygame.time.get_ticks() / 1000


def mezclar(c1, c2, t):

    t = max(0, min(1, t))

    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def oscurecer(color, factor=0.7):

    return tuple(int(c * factor) for c in color)


_halos = {}


def halo(color, radio, alfa=160):

    clave = (color, radio, alfa)

    if clave not in _halos:

        superficie = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)

        for r in range(radio, 0, -1):

            a = int(alfa * (1 - r / radio) ** 1.5)

            pygame.draw.circle(superficie, (*color, a), (radio, radio), r)

        _halos[clave] = superficie

    return _halos[clave]


def dibujar_halo(x, y, color, radio, alfa=160):

    pantalla.blit(halo(color, radio, alfa), (x - radio, y - radio))


def crear_fondo():

    fondo = pygame.Surface((ANCHO, ALTO))

    azar = random.Random(7)

    for y in range(HORIZONTE + 1):

        color = mezclar((10, 10, 28), (70, 40, 75), y / HORIZONTE)

        pygame.draw.line(fondo, color, (0, y), (ANCHO, y))

    for _ in range(80):

        x = azar.randint(0, ANCHO - 1)

        y = azar.randint(0, HORIZONTE - 25)

        brillo = azar.randint(110, 255)

        fondo.set_at((x, y), (brillo, brillo, brillo))

    luna = halo((255, 240, 200), 60, 90)

    fondo.blit(luna, (860 - 60, 62 - 60))

    pygame.draw.circle(fondo, (240, 235, 210), (860, 62), 14)

    pygame.draw.circle(fondo, (215, 210, 185), (855, 58), 4)

    pygame.draw.circle(fondo, (220, 215, 190), (865, 67), 3)

    x = -10

    while x < ANCHO:

        ancho = azar.randint(30, 70)

        alto = azar.randint(20, 55)

        pygame.draw.rect(
            fondo,
            (28, 22, 38),
            (x, HORIZONTE - alto, ancho, alto)
        )

        if azar.random() < 0.4:

            pygame.draw.polygon(
                fondo,
                (28, 22, 38),
                [
                    (x, HORIZONTE - alto),
                    (x + ancho // 2, HORIZONTE - alto - azar.randint(5, 15)),
                    (x + ancho, HORIZONTE - alto),
                ]
            )

        for _ in range(azar.randint(0, 5)):

            if azar.random() < 0.5:

                vx = x + azar.randint(4, ancho - 8)

                vy = HORIZONTE - alto + azar.randint(4, alto - 9)

                pygame.draw.rect(fondo, (210, 175, 80), (vx, vy, 4, 5))

        x += ancho + azar.randint(-5, 10)

    for y in range(HORIZONTE, ALTO):

        color = mezclar(
            (38, 44, 32),
            (18, 22, 16),
            (y - HORIZONTE) / (ALTO - HORIZONTE)
        )

        pygame.draw.line(fondo, color, (0, y), (ANCHO, y))

    for _ in range(500):

        x = azar.randint(0, ANCHO)

        y = azar.randint(HORIZONTE, ALTO)

        pygame.draw.line(
            fondo,
            (48, 60, 36),
            (x, y),
            (x + azar.randint(-2, 2), y - azar.randint(2, 6))
        )

    for c in CARRILES:

        pygame.draw.rect(fondo, (50, 48, 52), (0, c - 40, ANCHO, 80))

        for _ in range(500):

            x = azar.randint(0, ANCHO - 1)

            y = azar.randint(c - 39, c + 39)

            tono = azar.randint(40, 64)

            fondo.set_at((x, y), (tono, tono, tono + 4))

        for _ in range(5):

            x = azar.randint(60, ANCHO - 40)

            y = azar.randint(c - 30, c + 30)

            puntos = [(x, y)]

            for _ in range(4):

                x += azar.randint(4, 12)

                y += azar.randint(-5, 5)

                puntos.append((x, y))

            pygame.draw.lines(fondo, (32, 30, 34), False, puntos, 2)

        for x in range(0, ANCHO, 60):

            pygame.draw.rect(fondo, (120, 112, 80), (x + 10, c - 1, 28, 3))

        pygame.draw.line(fondo, (95, 90, 82), (0, c - 40), (ANCHO, c - 40), 3)

        pygame.draw.line(fondo, (95, 90, 82), (0, c + 40), (ANCHO, c + 40), 3)

    for c in CARRILES:

        for fila in range(3):

            for col in range(3):

                x = 2 + col * 15 + (7 if fila % 2 else 0)

                y = c + 26 - fila * 10

                pygame.draw.ellipse(fondo, (150, 130, 90), (x, y, 19, 12))

                pygame.draw.ellipse(fondo, (100, 85, 60), (x, y, 19, 12), 1)

    huecos = [
        (HORIZONTE + 2, CARRILES[0] - 42),
        (CARRILES[0] + 42, CARRILES[1] - 42),
        (CARRILES[1] + 42, CARRILES[2] - 42),
        (CARRILES[2] + 42, ALTO - 66),
    ]

    for arriba, abajo in huecos:

        if abajo - arriba < 6:

            continue

        for _ in range(7):

            x = azar.randint(80, ANCHO - 20)

            y = azar.randint(arriba + 4, abajo - 2)

            tipo = azar.random()

            if tipo < 0.4:

                pygame.draw.ellipse(fondo, (75, 72, 70), (x, y - 6, 14, 8))

                pygame.draw.ellipse(fondo, (95, 92, 88), (x + 2, y - 6, 8, 4))

            elif tipo < 0.75:

                for _ in range(5):

                    pygame.draw.line(
                        fondo,
                        (85, 70, 45),
                        (x, y),
                        (x + azar.randint(-8, 8), y - azar.randint(5, 12)),
                        1
                    )

            else:

                pygame.draw.rect(fondo, (100, 95, 100), (x, y - 14, 3, 14))

                pygame.draw.rect(fondo, (100, 95, 100), (x - 4, y - 11, 11, 3))

    return fondo.convert()


def crear_niebla():

    niebla = pygame.Surface((ANCHO * 2, ALTO), pygame.SRCALPHA)

    azar = random.Random(11)

    for _ in range(35):

        ancho = azar.randint(160, 340)

        alto = azar.randint(30, 70)

        x = azar.randint(0, ANCHO)

        y = azar.randint(HORIZONTE - 10, ALTO - 80)

        capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        pygame.draw.ellipse(capa, (190, 200, 210, azar.randint(8, 16)), capa.get_rect())

        niebla.blit(capa, (x, y))

        niebla.blit(capa, (x + ANCHO, y))

    return niebla


def crear_vineta():

    vineta = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

    for i in range(0, 70, 2):

        alfa = int(130 * (1 - i / 70) ** 2)

        pygame.draw.rect(
            vineta,
            (0, 0, 0, alfa),
            (i, i, ANCHO - 2 * i, ALTO - 2 * i),
            2
        )

    return vineta


def crear_sombra():

    sombra = pygame.Surface((34, 10), pygame.SRCALPHA)

    pygame.draw.ellipse(sombra, (0, 0, 0, 110), sombra.get_rect())

    return sombra


FONDO = crear_fondo()

NIEBLA = crear_niebla()

VINETA = crear_vineta()

SOMBRA = crear_sombra()


def dibujar_fondo():

    pantalla.blit(FONDO, (0, 0))

    desplazamiento = int(tiempo() * 12) % ANCHO

    pantalla.blit(NIEBLA, (-desplazamiento, 0))


def dibujar_vineta():

    pantalla.blit(VINETA, (0, 0))


def extremidad(color, inicio, angulo, largo, grosor, direccion=1):

    fin = (
        inicio[0] + math.sin(angulo) * largo * direccion,
        inicio[1] + math.cos(angulo) * largo
    )

    pygame.draw.line(pantalla, color, inicio, fin, grosor)

    pygame.draw.circle(pantalla, color, fin, grosor // 2)

    return fin


def dibujar_persona(
    cx,
    suelo,
    t,
    piel,
    ropa,
    direccion=1,
    zancada=0.0,
    velocidad=8.0,
    brazo_delantero=None,
    brazo_trasero=None,
    inclinacion=0.0,
    agachado=0.0,
    respiracion=True
):

    camisa, pantalon, pelo = ropa

    onda = math.sin(t * velocidad)

    paso = onda * zancada

    rebote = abs(onda) * 4 * zancada

    respira = math.sin(t * 2.5) if respiracion else 0

    pantalla.blit(SOMBRA, (cx - SOMBRA.get_width() // 2, suelo - 5))

    cadera = (cx, suelo - 24 + agachado - rebote)

    largo_pierna = 24 - agachado

    hombro = (
        cx + inclinacion * direccion,
        cadera[1] - 22 + respira
    )

    if brazo_trasero is None:

        brazo_trasero = paso * 0.9

    if brazo_delantero is None:

        brazo_delantero = -paso * 0.9

    mano_trasera = extremidad(
        oscurecer(camisa),
        hombro,
        brazo_trasero,
        17,
        6,
        direccion
    )

    pygame.draw.circle(pantalla, oscurecer(piel, 0.85), mano_trasera, 3)

    extremidad(oscurecer(pantalon), cadera, -paso, largo_pierna, 7, direccion)

    pie_trasero = (
        cadera[0] + math.sin(-paso) * largo_pierna * direccion,
        cadera[1] + math.cos(-paso) * largo_pierna
    )

    pygame.draw.ellipse(
        pantalla,
        (30, 25, 25),
        (pie_trasero[0] - 4 + 2 * direccion, pie_trasero[1] - 2, 9, 5)
    )

    extremidad(pantalon, cadera, paso, largo_pierna, 7, direccion)

    pie = (
        cadera[0] + math.sin(paso) * largo_pierna * direccion,
        cadera[1] + math.cos(paso) * largo_pierna
    )

    pygame.draw.ellipse(
        pantalla,
        (40, 32, 30),
        (pie[0] - 4 + 2 * direccion, pie[1] - 2, 9, 5)
    )

    pygame.draw.polygon(
        pantalla,
        camisa,
        [
            (cadera[0] - 7, cadera[1] + 2),
            (cadera[0] + 7, cadera[1] + 2),
            (hombro[0] + 8, hombro[1]),
            (hombro[0] - 8, hombro[1]),
        ]
    )

    pygame.draw.circle(pantalla, camisa, hombro, 8)

    pygame.draw.line(
        pantalla,
        oscurecer(pantalon, 0.6),
        (cadera[0] - 7, cadera[1]),
        (cadera[0] + 7, cadera[1]),
        3
    )

    cabeza = (
        hombro[0] + 2 * direccion,
        hombro[1] - 12
    )

    pygame.draw.circle(pantalla, piel, cabeza, 9)

    pygame.draw.circle(
        pantalla,
        pelo,
        cabeza,
        9,
        draw_top_left=True,
        draw_top_right=True,
        draw_bottom_left=direccion == 1,
        draw_bottom_right=direccion == -1
    )

    pygame.draw.circle(
        pantalla,
        piel,
        (cabeza[0] + 3 * direccion, cabeza[1] + 2),
        6
    )

    ojo = (cabeza[0] + 5 * direccion, cabeza[1] + 1)

    mano = extremidad(
        camisa,
        hombro,
        brazo_delantero,
        17,
        6,
        direccion
    )

    pygame.draw.circle(pantalla, piel, mano, 3)

    return {
        "cabeza": cabeza,
        "ojo": ojo,
        "mano": mano,
        "hombro": hombro,
    }


def dibujar_fogonazo(x, y, ultimo_disparo, direccion=1):

    edad = pygame.time.get_ticks() - ultimo_disparo

    if edad > 80:

        return

    escala = 1 - edad / 80

    dibujar_halo(x, y, (255, 200, 80), int(22 * escala) + 4, 200)

    largo = 14 * escala + 4

    pygame.draw.polygon(
        pantalla,
        (255, 240, 150),
        [
            (x, y - 4 * escala),
            (x + largo * direccion, y),
            (x, y + 4 * escala),
        ]
    )


def etiqueta(texto, cx, cy, color):

    render = fuentePequena.render(texto, True, BLANCO)

    rect = render.get_rect(center=(int(cx), int(cy)))

    caja = rect.inflate(14, 6)

    superficie = pygame.Surface(caja.size, pygame.SRCALPHA)

    pygame.draw.rect(
        superficie,
        (14, 14, 22, 200),
        superficie.get_rect(),
        border_radius=8
    )

    pygame.draw.rect(
        superficie,
        color,
        superficie.get_rect(),
        1,
        border_radius=8
    )

    pantalla.blit(superficie, caja.topleft)

    pantalla.blit(render, rect)


def barra_vida(cx, y, fraccion, ancho=34):

    fraccion = max(0, min(1, fraccion))

    x = int(cx - ancho / 2)

    pygame.draw.rect(pantalla, (20, 20, 25), (x - 1, y - 1, ancho + 2, 7), border_radius=3)

    if fraccion > 0:

        pygame.draw.rect(
            pantalla,
            mezclar(ROJO, VERDE, fraccion),
            (x, y, int(ancho * fraccion), 5),
            border_radius=2
        )

    pygame.draw.line(
        pantalla,
        (255, 255, 255),
        (x + 1, y + 1),
        (x + max(1, int(ancho * fraccion)) - 2, y + 1)
    )


def dibujar_tumba(cx, suelo):

    pygame.draw.ellipse(pantalla, (55, 45, 35), (cx - 18, suelo - 6, 36, 10))

    pygame.draw.rect(
        pantalla,
        (115, 115, 125),
        (cx - 11, suelo - 30, 22, 28),
        border_top_left_radius=10,
        border_top_right_radius=10
    )

    pygame.draw.rect(
        pantalla,
        (80, 80, 90),
        (cx - 11, suelo - 30, 22, 28),
        2,
        border_top_left_radius=10,
        border_top_right_radius=10
    )

    texto = fuentePequena.render("RIP", True, (50, 50, 55))

    pantalla.blit(texto, texto.get_rect(center=(cx, suelo - 16)))


def dibujar_jugador(jugador):

    c = CARRILES[jugador.carril]

    cx = jugador.x + 15

    suelo = c + 35

    t = tiempo() + jugador.fase

    puntos = dibujar_persona(
        cx,
        suelo,
        t,
        PIEL_HUMANA,
        ROPA_JUGADOR,
        brazo_delantero=math.pi / 2,
        brazo_trasero=math.pi / 2 - 0.35
    )

    cabeza = puntos["cabeza"]

    pygame.draw.circle(
        pantalla,
        (70, 88, 60),
        (cabeza[0], cabeza[1] - 1),
        11,
        draw_top_left=True,
        draw_top_right=True
    )

    pygame.draw.line(
        pantalla,
        (50, 65, 45),
        (cabeza[0] - 11, cabeza[1] - 1),
        (cabeza[0] + 14, cabeza[1] - 1),
        3
    )

    mano = puntos["mano"]

    pygame.draw.line(pantalla, (90, 60, 35), (mano[0] - 18, mano[1] + 3), (mano[0] - 4, mano[1] + 1), 6)

    pygame.draw.line(pantalla, (45, 45, 52), (mano[0] - 6, mano[1]), (mano[0] + 18, mano[1]), 5)

    pygame.draw.line(pantalla, (35, 35, 40), (mano[0] + 18, mano[1]), (mano[0] + 30, mano[1]), 3)

    pygame.draw.line(pantalla, (35, 35, 40), (mano[0] + 4, mano[1] + 2), (mano[0] + 4, mano[1] + 8), 3)

    dibujar_fogonazo(mano[0] + 32, mano[1], jugador.ultimoDisparo)

    etiqueta("JUGADOR", cx, c - 54, AZUL)


def dibujar_superviviente(superviviente):

    c = CARRILES[superviviente.carril]

    cx = superviviente.x + 15

    suelo = c + 35

    if superviviente.vida <= 0:

        dibujar_tumba(cx, suelo)

        return

    t = tiempo() + superviviente.fase

    ropa = ROPA_SUPERVIVIENTES[superviviente.carril % len(ROPA_SUPERVIVIENTES)]

    estado = superviviente.estado

    if estado == "HUYENDO":

        puntos = dibujar_persona(
            cx, suelo, t, PIEL_HUMANA, ropa,
            direccion=-1,
            zancada=0.7,
            velocidad=16,
            inclinacion=3
        )

        cabeza = puntos["cabeza"]

        salto = abs(math.sin(t * 8)) * 3

        texto = fuente.render("!", True, AMARILLO)

        pantalla.blit(texto, texto.get_rect(center=(cabeza[0] + 14, cabeza[1] - 10 - salto)))

    elif estado == "HERIDO":

        parpadeo = int(t * 10) % 2 == 0

        puntos = dibujar_persona(
            cx, suelo, t,
            PIEL_HERIDA if parpadeo else PIEL_HUMANA,
            ropa,
            agachado=6,
            inclinacion=-3,
            brazo_delantero=0.6,
            brazo_trasero=-0.2
        )

        cabeza = puntos["cabeza"]

        pygame.draw.line(
            pantalla,
            (240, 240, 235),
            (cabeza[0] - 9, cabeza[1] - 4),
            (cabeza[0] + 9, cabeza[1] - 6),
            3
        )

    elif estado == "A_SALVO":

        puntos = dibujar_persona(
            cx, suelo, t, PIEL_HUMANA, ropa,
            brazo_delantero=0.15,
            brazo_trasero=-0.1
        )

        cabeza = puntos["cabeza"]

        brillo = 0.5 + 0.5 * math.sin(t * 4)

        dibujar_halo(cx, suelo - 25, MORADO, 34, int(40 + 40 * brillo))

        x, y = cabeza[0] + 16, cabeza[1] - 8

        pygame.draw.polygon(
            pantalla,
            MORADO,
            [(x - 6, y - 6), (x + 6, y - 6), (x + 6, y), (x, y + 7), (x - 6, y)]
        )

        pygame.draw.polygon(
            pantalla,
            BLANCO,
            [(x - 6, y - 6), (x + 6, y - 6), (x + 6, y), (x, y + 7), (x - 6, y)],
            1
        )

    else:

        puntos = dibujar_persona(
            cx, suelo, t, PIEL_HUMANA, ropa,
            brazo_delantero=math.pi / 2,
            brazo_trasero=math.pi / 2 - 0.45
        )

        mano = puntos["mano"]

        pygame.draw.line(pantalla, (50, 50, 58), (mano[0] - 2, mano[1]), (mano[0] + 11, mano[1]), 4)

        pygame.draw.line(pantalla, (40, 40, 46), (mano[0], mano[1]), (mano[0] - 1, mano[1] + 6), 3)

        dibujar_fogonazo(mano[0] + 13, mano[1], superviviente.ultimoDisparo)

    barra_vida(cx, c - 40, superviviente.vida / 50)

    etiqueta(
        estado,
        cx,
        c + 45,
        COLOR_ESTADO_SUPERVIVIENTE.get(estado, BLANCO)
    )

    # TEORÍA DE JUEGOS:
    # Se dibuja aparte del estado del autómata para dejar
    # claro que CAMINAR/HUYENDO es el estado y que
    # DISPARAR/HUIR es la estrategia elegida por Nash.
    if superviviente.ultimaEstrategia:

        etiqueta(
            f"TJ: {superviviente.ultimaEstrategia}",
            cx,
            c + 64,
            COLOR_ESTRATEGIA_JUEGO.get(
                superviviente.ultimaEstrategia,
                BLANCO
            )
        )


def dibujar_zombie(zombie):

    c = CARRILES[zombie.carril]

    cx = zombie.x + 15

    suelo = c + 35

    t = tiempo() + zombie.fase

    estado = zombie.estado

    frenesi = (
        estado == "ATACANDO"
        and zombie.ultimaDecision == "FRENESI"
    )

    tambaleo = math.sin(t * 3) * 0.12

    zancada = 0.0

    velocidad = 6.0

    brazo_d = math.pi / 2 - 0.15 + tambaleo

    brazo_t = math.pi / 2 - 0.3 - tambaleo

    inclinacion = 3.0

    if estado == "VAGANDO":

        zancada = 0.35

        velocidad = 4.0

    elif estado == "LLEGANDO":

        zancada = 0.5

        velocidad = 6.5

        inclinacion = 5.0

    elif estado == "ATACANDO":

        golpe = math.sin(t * (16 if frenesi else 9))

        brazo_d = math.pi / 2 + golpe * 0.6

        brazo_t = math.pi / 2 - golpe * 0.6

        inclinacion = 4 + golpe * 3

    elif estado == "ESPERANDO":

        brazo_d = math.pi / 3 + tambaleo

        brazo_t = math.pi / 3 - tambaleo

        inclinacion = 2.0

    elif estado == "RETROCEDIENDO":

        zancada = 0.4

        velocidad = -7.0

        brazo_d = math.pi / 4

        brazo_t = math.pi / 5

        inclinacion = -2.0

    if frenesi:

        pulso = 0.5 + 0.5 * math.sin(t * 12)

        dibujar_halo(cx, suelo - 28, (255, 40, 30), 40, int(70 + 70 * pulso))

    puntos = dibujar_persona(
        cx,
        suelo,
        t,
        PIEL_ZOMBIE,
        ROPA_ZOMBIE,
        direccion=-1,
        zancada=zancada,
        velocidad=velocidad,
        brazo_delantero=brazo_d,
        brazo_trasero=brazo_t,
        inclinacion=inclinacion,
        respiracion=False
    )

    hombro = puntos["hombro"]

    pygame.draw.circle(pantalla, (120, 30, 30), (hombro[0] + 2, hombro[1] + 10), 3)

    pygame.draw.circle(pantalla, (120, 30, 30), (hombro[0] - 3, hombro[1] + 15), 2)

    ojo = puntos["ojo"]

    dibujar_halo(ojo[0], ojo[1], (255, 50, 30), 8, 180)

    pygame.draw.circle(pantalla, (255, 90, 60), ojo, 2)

    cabeza = puntos["cabeza"]

    pygame.draw.line(
        pantalla,
        (60, 30, 30),
        (cabeza[0] - 6, cabeza[1] + 5),
        (cabeza[0] - 2, cabeza[1] + 5),
        2
    )

    barra_vida(cx, c - 40, zombie.vida / 200)

    texto_estado = estado

    if zombie.ultimaDecision:

        texto_estado += f" [{zombie.ultimaDecision}]"

    etiqueta(
        texto_estado,
        cx,
        c - 54,
        COLOR_ESTADO_ZOMBIE.get(estado, BLANCO)
    )

    # TEORÍA DE JUEGOS:
    # La estrategia aparece debajo del zombie mientras está activa
    # y permanece separada de VAGANDO/LLEGANDO/ATACANDO, que
    # pertenecen al autómata.
    if zombie.ultimaEstrategiaJuego:

        etiqueta(
            f"TJ: {zombie.ultimaEstrategiaJuego}",
            cx,
            c + 50,
            COLOR_ESTRATEGIA_JUEGO.get(
                zombie.ultimaEstrategiaJuego,
                BLANCO
            )
        )

    if zombie.automata.observaciones:

        estimacion = zombie.automata.estimacion

        probabilidad = zombie.automata.creencia_actual[estimacion]

        etiqueta(
            f"HMM: {estimacion} {probabilidad * 100:.0f}%",
            cx,
            c - 73,
            COLOR_HUMOR.get(estimacion, BLANCO)
        )


def dibujar_bala(x, carril, dano):

    y = CARRILES[carril] - 11

    fuerte = dano >= 20

    color = (255, 210, 90) if fuerte else (170, 225, 255)

    largo = 28 if fuerte else 16

    pygame.draw.line(
        pantalla,
        oscurecer(color, 0.5),
        (x - largo, y),
        (x - largo // 2, y),
        2
    )

    pygame.draw.line(pantalla, color, (x - largo // 2, y), (x, y), 3 if fuerte else 2)

    dibujar_halo(int(x), y, color, 12 if fuerte else 8, 150)

    pygame.draw.circle(pantalla, (255, 255, 240), (int(x), y), 3 if fuerte else 2)


particulas = []


def salpicar(x, y, color, cantidad=8, fuerza=120):

    for _ in range(cantidad):

        angulo = random.uniform(0, 2 * math.pi)

        rapidez = random.uniform(0.3, 1) * fuerza

        particulas.append([
            x,
            y,
            math.cos(angulo) * rapidez,
            math.sin(angulo) * rapidez - fuerza * 0.5,
            random.uniform(0.35, 0.8),
            color,
            random.randint(2, 4),
        ])


def actualizar_particulas(dt):

    for particula in particulas[:]:

        particula[0] += particula[2] * dt

        particula[1] += particula[3] * dt

        particula[3] += 420 * dt

        particula[4] -= dt

        if particula[4] <= 0:

            particulas.remove(particula)


def dibujar_particulas():

    for x, y, _, _, vida, color, radio in particulas:

        pygame.draw.circle(
            pantalla,
            color,
            (int(x), int(y)),
            max(1, int(radio * min(1, vida * 3)))
        )


def limpiar_particulas():

    particulas.clear()


def tecla(texto, x, y):

    render = fuentePequena.render(texto, True, BLANCO)

    caja = pygame.Rect(x, y, render.get_width() + 12, 20)

    pygame.draw.rect(pantalla, (45, 45, 58), caja, border_radius=4)

    pygame.draw.rect(pantalla, (120, 120, 140), caja, 1, border_radius=4)

    pantalla.blit(render, render.get_rect(center=caja.center))

    return caja.right


def texto_suave(texto, x, y, color=BLANCO, letra=None):

    letra = letra or fuentePequena

    render = letra.render(texto, True, color)

    pantalla.blit(render, (x, y))

    return x + render.get_width()


def dibujar_hud(eliminados, objetivo):

    barra = pygame.Surface((ANCHO, 44), pygame.SRCALPHA)

    barra.fill((10, 10, 16, 175))

    pygame.draw.line(barra, (255, 255, 255, 40), (0, 43), (ANCHO, 43))

    pantalla.blit(barra, (0, 0))

    pygame.draw.circle(pantalla, (225, 225, 215), (24, 20), 10)

    pygame.draw.rect(pantalla, (225, 225, 215), (18, 24, 12, 8), border_radius=2)

    pygame.draw.circle(pantalla, (20, 20, 25), (20, 19), 3)

    pygame.draw.circle(pantalla, (20, 20, 25), (28, 19), 3)

    for i in range(3):

        pygame.draw.line(pantalla, (20, 20, 25), (20 + i * 4, 27), (20 + i * 4, 31))

    texto = fuente.render(
        f"Zombies eliminados  {eliminados}/{objetivo}",
        True,
        BLANCO
    )

    pantalla.blit(texto, (44, 3))

    pygame.draw.rect(pantalla, (55, 55, 68), (44, 27, 220, 8), border_radius=4)

    progreso = eliminados / objetivo if objetivo else 0

    if progreso > 0:

        pygame.draw.rect(
            pantalla,
            VERDE,
            (44, 27, int(220 * progreso), 8),
            border_radius=4
        )

    x = 520

    x = tecla("W", x, 12) + 4

    x = tecla("S", x, 12) + 6

    x = texto_suave("carril", x, 15, (200, 200, 210)) + 16

    x = tecla("ESPACIO", x, 12) + 6

    x = texto_suave("disparar", x, 15, (200, 200, 210)) + 16

    x = tecla("R", x, 12) + 6

    texto_suave("reiniciar", x, 15, (200, 200, 210))


def dibujar_panel_inferior(lineas):

    panel = pygame.Surface((ANCHO, 64), pygame.SRCALPHA)

    panel.fill((10, 10, 16, 185))

    pygame.draw.line(panel, (255, 255, 255, 40), (0, 0), (ANCHO, 0))

    pantalla.blit(panel, (0, ALTO - 64))

    for i, (texto, color) in enumerate(lineas):

        pygame.draw.circle(pantalla, color, (20, ALTO - 50 + i * 26), 4)

        render = fuente.render(texto, True, BLANCO)

        pantalla.blit(render, (32, ALTO - 61 + i * 26))


def dibujar_final(victoria):

    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

    capa.fill((0, 0, 0, 150))

    pantalla.blit(capa, (0, 0))

    mensaje = "¡GANASTE!" if victoria else "PERDISTE"

    color = VERDE if victoria else ROJO

    centro = (ANCHO // 2, ALTO // 2 - 30)

    dibujar_halo(centro[0], centro[1], color, 160, 70)

    sombra = fuenteEnorme.render(mensaje, True, (0, 0, 0))

    pantalla.blit(sombra, sombra.get_rect(center=(centro[0] + 4, centro[1] + 4)))

    titulo = fuenteEnorme.render(mensaje, True, color)

    pantalla.blit(titulo, titulo.get_rect(center=centro))

    pulso = 0.5 + 0.5 * math.sin(tiempo() * 4)

    sub = fuente.render("Presiona R para reiniciar", True, BLANCO)

    sub.set_alpha(int(120 + 135 * pulso))

    pantalla.blit(sub, sub.get_rect(center=(centro[0], centro[1] + 60)))
