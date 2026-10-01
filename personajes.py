import pygame
import random

from config import CARRILES

import graficos

from automatas import (
    AutomataZombie,
    AutomataSuperviviente
)

from teoria_juegos import (
    decidir_enfrentamiento
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

        # TEORÍA DE JUEGOS
        # Controla cada cuánto se vuelve a decidir
        # una estrategia contra el zombie cercano.
        self.cooldownEstrategia = 0

        self.ultimaEstrategia = ""

        self.ultimoEquilibrio = ""

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

        self.cooldownEstrategia -= dt


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

                    # TEORÍA DE JUEGOS:
                    # Cuando el zombie entra en la zona de
                    # enfrentamiento, ambos agentes eligen
                    # estrategias mediante un juego 2x2.

                    if (
                        self.cooldownEstrategia <= 0
                        and zombie.cooldownEstrategiaJuego <= 0
                    ):

                        resultado = decidir_enfrentamiento(
                            self,
                            zombie,
                            distancia
                        )

                        self.ultimaEstrategia = (
                            resultado["superviviente"]
                        )

                        self.ultimoEquilibrio = (
                            resultado["tipo"]
                        )

                        # La decisión del zombie se aplica como una
                        # acción estratégica temporal. ESQUIVAR cambia
                        # de carril; ATACAR mantiene su avance normal.
                        zombie.aplicar_estrategia_juego(
                            resultado["zombie"]
                        )

                        # No se recalcula en cada frame.
                        self.cooldownEstrategia = 1.0


                    # Ejecutar la estrategia elegida por
                    # el superviviente.

                    if self.ultimaEstrategia == "HUIR":

                        self.automata.cambiar_estado(
                            "detecta_zombie"
                        )

                    elif (
                        self.ultimaEstrategia == "DISPARAR"
                        and self.cooldown <= 0
                    ):

                        balas.append([
                            self.x,
                            self.carril,
                            5
                        ])

                        self.ultimoDisparo = pygame.time.get_ticks()

                        self.cooldown = 1.5

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

        # TEORÍA DE JUEGOS
        # Estrategia elegida en el enfrentamiento actual.
        self.ultimaEstrategiaJuego = ""

        # Tiempo durante el cual se muestra la estrategia en pantalla.
        self.tiempoEstrategiaJuego = 0

        # Evita que varios supervivientes obliguen al mismo zombie a
        # recalcular/cambiar de carril varias veces en el mismo instante.
        self.cooldownEstrategiaJuego = 0

        self.fase = random.uniform(0, 10)


    @property
    def estado(self):

        return self.automata.estado


    # ACCIÓN ESTRATÉGICA DE TEORÍA DE JUEGOS

    def aplicar_estrategia_juego(
        self,
        estrategia,
        duracion=0.8
    ):

        self.ultimaEstrategiaJuego = estrategia

        self.tiempoEstrategiaJuego = duracion

        # Bloquea nuevas decisiones sobre este zombie por un instante.
        self.cooldownEstrategiaJuego = 0.9

        if estrategia == "ESQUIVAR":

            self.esquivar()


    def esquivar(self):
        """
        Cambia a un carril adyacente para salir de la línea de tiro.
        No modifica el estado del autómata: un zombie puede seguir
        LLEGANDO o VAGANDO mientras ejecuta esta acción estratégica.
        """

        carriles_posibles = []

        if self.carril > 0:
            carriles_posibles.append(
                self.carril - 1
            )

        if self.carril < 2:
            carriles_posibles.append(
                self.carril + 1
            )

        if carriles_posibles:
            self.carril = random.choice(
                carriles_posibles
            )


    # ACTUALIZAR

    def actualizar(
        self,
        supervivientes,
        dt
    ):

        # TEORÍA DE JUEGOS:
        # La estrategia solo permanece visible durante un instante.
        # ESQUIVAR ya cambió el carril al momento de ser seleccionada;
        # después el autómata continúa funcionando normalmente.

        if self.cooldownEstrategiaJuego > 0:
            self.cooldownEstrategiaJuego = max(
                0,
                self.cooldownEstrategiaJuego - dt
            )

        if self.tiempoEstrategiaJuego > 0:
            self.tiempoEstrategiaJuego -= dt

            if self.tiempoEstrategiaJuego <= 0:
                self.ultimaEstrategiaJuego = ""

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
