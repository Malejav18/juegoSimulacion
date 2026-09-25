import pygame
import random

from config import (
    pantalla,
    CARRILES,
    ANCHO,
    fuente,
    BLANCO,
    ROJO,
    VERDE,
    AZUL,
    AMARILLO,
    NARANJA,
    MORADO,
    CIAN
)

from automatas import (
    AutomataZombie,
    AutomataSuperviviente
)


# JUGADOR

class Jugador:

    def __init__(self):

        self.x = 60
        self.carril = 1
        self.vida = 100


    def subir(self):

        self.carril = max(
            0,
            self.carril - 1
        )


    def bajar(self):

        self.carril = min(
            2,
            self.carril + 1
        )


    def disparar(self):

        return [
            self.x,
            self.carril,
            30
        ]


    def dibujar(self):

        y = CARRILES[self.carril]

        pygame.draw.rect(
            pantalla,
            AZUL,
            (self.x, y - 20, 30, 40)
        )

        texto = fuente.render(
            "JUGADOR",
            True,
            BLANCO
        )

        pantalla.blit(
            texto,
            (self.x - 15, y - 45)
        )


# SUPERVIVIENTE

class Superviviente:

    def __init__(self, carril):

        self.x = 250

        self.carril = carril

        self.vida = 50

        self.cooldown = 0

        self.tiempoEstado = 0

        # Cada superviviente tiene
        # su propio autómata

        self.automata = (
            AutomataSuperviviente()
        )

    @property
    def porcentaje_vida(self):
        return (self.vida / 50) * 100

    @property
    def estado(self):
        return self.automata.estado


    # ACTUALIZAR

    def actualizar(
        self,
        zombies,
        balas,
        dt
    ):

        self.cooldown -= dt


        # HERIDO

        if self.estado == "HERIDO":

            self.tiempoEstado -= dt

            if self.tiempoEstado <= 0:

                self.automata.cambiar_estado(
                    "recupera"
                )

                self.tiempoEstado = 1

            return


        # A SALVO

        if self.estado == "A_SALVO":

            self.tiempoEstado -= dt

            if self.tiempoEstado <= 0:

                self.automata.cambiar_estado(
                    "no_hay_zombie"
                )

            return


        # BUSCAR ZOMBIES

        cercanos = [

            zombie

            for zombie in zombies

            if (
                zombie.carril
                == self.carril
                and zombie.x > self.x
                and zombie.vida > 0
            )
        ]


        # HAY ZOMBIES

        if cercanos:

            zombie = min(
                cercanos,
                key=lambda z: z.x
            )

            distancia = (
                zombie.x - self.x
            )


            # CAMINAR

            if self.estado == "CAMINAR":

                if distancia < 150:

                    self.automata.cambiar_estado(
                        "detecta_zombie"
                    )

                else:

                    # Dispara automáticamente

                    if self.cooldown <= 0:

                        balas.append([
                            self.x,
                            self.carril,
                            5
                        ])

                        self.cooldown = 1.5


            # HUYENDO

            elif self.estado == "HUYENDO":

                self.x -= 10 * dt

                self.x = max(
                    150,
                    self.x
                )

                if distancia > 220:

                    self.automata.cambiar_estado(
                        "logra_huir"
                    )

                    self.tiempoEstado = 1


        # NO HAY ZOMBIES

        else:

            if self.estado == "HUYENDO":

                self.automata.cambiar_estado(
                    "logra_huir"
                )

                self.tiempoEstado = 1


    # RECIBIR DAÑO

    def recibir_dano(self, dano=10):
        # Estado actual
        vida_actual = self.vida

        # Ecuación del sistema dinámico:
        # V(n+1) = max(0, V(n) - D(n))
        nueva_vida = max(
            0,
            vida_actual - dano
        )

        # Actualizar el estado
        self.vida = nueva_vida

        # Cambiar el estado del autómata
        if self.estado != "HUYENDO":
            self.automata.estado = "HUYENDO"

        self.automata.cambiar_estado(
            "es_atacado"
        )

        self.tiempoEstado = 1

    # DIBUJAR

    def dibujar(self):

        if self.vida <= 0:
            return

        y = CARRILES[self.carril]

        color = VERDE

        if self.estado == "HUYENDO":

            color = AMARILLO

        elif self.estado == "HERIDO":

            color = ROJO

        elif self.estado == "A_SALVO":

            color = MORADO


        pygame.draw.rect(
            pantalla,
            color,
            (self.x, y - 20, 30, 40)
        )


        # Estado

        texto = fuente.render(
            self.estado,
            True,
            BLANCO
        )

        pantalla.blit(
            texto,
            (self.x - 20, y - 45)
        )


        # Vida

        vidaTexto = fuente.render(
            f"Vida: {self.porcentaje_vida:.0f}%",
            True,
            BLANCO
        )

        pantalla.blit(
            vidaTexto,
            (self.x + 5, y + 25)
        )


# ZOMBIE

class Zombie:

    def __init__(self):

        self.x = 750

        self.carril = random.randint(
            0,
            2
        )

        self.vida = 200

        self.cooldown = 0

        # Cada zombie tiene
        # su propio autómata

        self.automata = AutomataZombie()

        # Última decisión de la cadena de Markov

        self.ultimaDecision = ""


    @property
    def estado(self):

        return self.automata.estado


    # ACTUALIZAR

    def actualizar(
        self,
        supervivientes,
        dt
    ):

        # Buscar supervivientes vivos
        # en el mismo carril

        posibles = [

            superviviente

            for superviviente
            in supervivientes

            if (
                superviviente.carril
                == self.carril

                and superviviente.vida > 0
            )
        ]


        # SIN OBJETIVO

        if not posibles:

            self.automata.estado = "VAGANDO"

            self.x -= 30 * dt

            return


        objetivo = posibles[0]

        distancia = (
            self.x - objetivo.x
        )


        # VAGANDO

        if self.estado == "VAGANDO":

            self.x -= 30 * dt

            if distancia < 250:

                self.automata.cambiar_estado(
                    "detecta_jugador"
                )


        # LLEGANDO

        elif self.estado == "LLEGANDO":

            self.x -= 40 * dt

            if distancia < 45:

                self.automata.cambiar_estado(
                    "llega_objetivo"
                )

                self.cooldown = 1


        # ATACANDO

        elif self.estado == "ATACANDO":

            self.cooldown -= dt

            if self.cooldown <= 0:

                objetivo.recibir_dano()

                # CADENA DE MARKOV:
                # decide qué hace después del ataque

                decision = self.automata.terminar_ataque()

                self.ultimaDecision = decision

                if decision == "FRENESI":

                    # Vuelve a atacar más rápido
                    self.cooldown = 0.5

                elif decision == "RETROCEDER":

                    self.cooldown = 0.8

                else:

                    self.cooldown = 1


        # RETROCEDIENDO

        elif self.estado == "RETROCEDIENDO":

            self.x += 60 * dt

            self.cooldown -= dt

            if self.cooldown <= 0:

                self.automata.cambiar_estado(
                    "termina_retroceso"
                )


        # ESPERANDO

        elif self.estado == "ESPERANDO":

            self.cooldown -= dt

            if self.cooldown <= 0:

                self.automata.cambiar_estado(
                    "turno_disponible"
                )


    # DIBUJAR

    def dibujar(self):

        y = CARRILES[self.carril]

        color = ROJO


        if self.estado == "VAGANDO":

            color = ROJO


        elif self.estado == "LLEGANDO":

            color = NARANJA


        elif self.estado == "ATACANDO":

            color = MORADO


        elif self.estado == "ESPERANDO":

            color = AMARILLO


        elif self.estado == "RETROCEDIENDO":

            color = CIAN


        pygame.draw.rect(
            pantalla,
            color,
            (self.x, y - 20, 30, 40)
        )


        # Estado (y decisión de Markov si hubo)

        etiqueta = self.estado

        if self.ultimaDecision:

            etiqueta += f" [{self.ultimaDecision}]"

        texto = fuente.render(
            etiqueta,
            True,
            BLANCO
        )

        pantalla.blit(
            texto,
            (self.x - 20, y - 45)
        )


        # Vida

        vidaTexto = fuente.render(
            str(self.vida),
            True,
            BLANCO
        )

        pantalla.blit(
            vidaTexto,
            (self.x + 2, y + 25)
        )