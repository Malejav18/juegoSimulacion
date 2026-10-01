import pygame
import random

from config import CARRILES

import graficos

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
        self.fase = random.uniform(0, 10)
        self.ultimoDisparo = -1000


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

        self.ultimoDisparo = pygame.time.get_ticks()

        return [
            self.x,
            self.carril,
            30
        ]


    def dibujar(self):

        graficos.dibujar_jugador(self)


# SUPERVIVIENTE

class Superviviente:

    def __init__(self, carril):

        self.x = 250

        self.carril = carril

        self.vida = 50

        self.cooldown = 0

        self.tiempoEstado = 0

        self.fase = random.uniform(0, 10)

        self.ultimoDisparo = -1000

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

                umbral = 150

                if zombie.automata.creencia_actual["FURIOSO"] > 0.5:

                    umbral = 200

                if distancia < umbral:

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

                        self.ultimoDisparo = pygame.time.get_ticks()

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

        graficos.salpicar(
            self.x + 15,
            CARRILES[self.carril] - 10,
            graficos.SANGRE_HUMANA,
            10
        )

        # Cambiar el estado del autómata
        if self.estado != "HUYENDO":
            self.automata.estado = "HUYENDO"

        self.automata.cambiar_estado(
            "es_atacado"
        )

        self.tiempoEstado = 1

    # DIBUJAR

    def dibujar(self):

        graficos.dibujar_superviviente(self)


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

        self.fase = random.uniform(0, 10)


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

        graficos.dibujar_zombie(self)
