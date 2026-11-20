import pygame

from config import (
    reloj,
    FPS,
    ANCHO,
    CARRILES,
    MORADO,
    CIAN,
    VERDE
)

from genetico import AlgoritmoGenetico

import graficos

from personajes import (
    Jugador,
    Superviviente,
    Zombie
)

from automatas import AutomataZombie

from markov import crear_hmm_zombie


ESTACIONARIA = (
    crear_hmm_zombie()
    .distribucion_observaciones()
)


# JUEGO

class Juego:

    def __init__(self):

        self.reiniciar()


    # REINICIAR

    def reiniciar(self):

        self.jugador = Jugador()

        self.supervivientes = [

            Superviviente(0),
            Superviviente(1),
            Superviviente(2)
        ]

        self.zombies = []

        self.balas = []

        self.tiempoZombie = 0

        self.eliminados = 0

        self.objetivo = 10

        self.juegoTerminado = False

        self.victoria = False

        AutomataZombie.reiniciar_estadisticas()

        graficos.limpiar_particulas()

        self.viterbiInferencias = -1

        self.viterbiResultado = (0, 0)

        self.evolucion = AlgoritmoGenetico()


    # EVENTOS

    def eventos(self):

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                return False


            if evento.type == pygame.KEYDOWN:


                # Mientras esté jugando

                if not self.juegoTerminado:


                    if evento.key == pygame.K_w:

                        self.jugador.subir()


                    elif evento.key == pygame.K_s:

                        self.jugador.bajar()


                    elif evento.key == pygame.K_SPACE:

                        self.balas.append(
                            self.jugador.disparar()
                        )


                # Reiniciar partida

                if evento.key == pygame.K_r:

                    if self.juegoTerminado:

                        self.reiniciar()


        return True


    # ACTUALIZAR

    def actualizar(self, dt):

        graficos.actualizar_particulas(dt)

        # Si terminó, nada se mueve

        if self.juegoTerminado:

            return


        # CREAR ZOMBIES

        self.tiempoZombie += dt

        if self.tiempoZombie > 3:

            self.zombies.append(
                Zombie(
                    self.evolucion.nuevo_genoma(),
                    self.evolucion.generacion
                )
            )

            self.tiempoZombie = 0


        # SUPERVIVIENTES

        for superviviente in self.supervivientes:

            if superviviente.vida > 0:

                superviviente.actualizar(
                    self.zombies,
                    self.balas,
                    dt
                )


        # ZOMBIES

        for zombie in self.zombies:

            zombie.actualizar(
                self.supervivientes,
                self.balas,
                self.jugador,
                dt
            )


        # BALAS

        self.actualizar_balas(dt)


        # ELIMINAR ZOMBIES

        for zombie in self.zombies[:]:

            if zombie.vida <= 0:

                graficos.salpicar(
                    zombie.x + 15,
                    CARRILES[zombie.carril] - 10,
                    graficos.SANGRE_ZOMBIE,
                    28,
                    200
                )

                self.zombies.remove(
                    zombie
                )

                self.eliminados += 1

                self.evolucion.evaluar(zombie)

            elif zombie.x < -40:

                self.zombies.remove(
                    zombie
                )

                self.evolucion.evaluar(zombie, escapo=True)


        # VICTORIA

        if self.eliminados >= self.objetivo:

            self.eliminados = self.objetivo

            self.juegoTerminado = True

            self.victoria = True


        # DERROTA

        vivos = [

            superviviente

            for superviviente
            in self.supervivientes

            if superviviente.vida > 0
        ]


        if len(vivos) == 0:

            self.juegoTerminado = True

            self.victoria = False


    # BALAS

    def actualizar_balas(self, dt):

        for bala in self.balas[:]:

            # Movimiento

            bala[0] += 400 * dt


            # Revisar colisión

            for zombie in self.zombies:

                if (
                    zombie.carril
                    == bala[1]

                    and abs(
                        zombie.x
                        - bala[0]
                    ) < 20
                ):

                    zombie.vida -= bala[2]

                    graficos.salpicar(
                        zombie.x + 10,
                        CARRILES[zombie.carril] - 11,
                        graficos.SANGRE_ZOMBIE,
                        8 if bala[2] >= 20 else 3
                    )

                    if bala in self.balas:

                        self.balas.remove(
                            bala
                        )

                    break


            # Salió de pantalla

            if (
                bala in self.balas
                and bala[0] > ANCHO
            ):

                self.balas.remove(
                    bala
                )


    # DIBUJAR

    def dibujar(self):

        graficos.dibujar_fondo()

        for carril in range(len(CARRILES)):

            for superviviente in self.supervivientes:

                if superviviente.carril == carril:

                    superviviente.dibujar()

            for zombie in sorted(self.zombies, key=lambda z: -z.x):

                if zombie.carril == carril:

                    zombie.dibujar()

            if self.jugador.carril == carril:

                self.jugador.dibujar()

        for bala in self.balas:

            graficos.dibujar_bala(bala[0], bala[1], bala[2])

        graficos.dibujar_particulas()

        graficos.dibujar_vineta()

        graficos.dibujar_hud(self.eliminados, self.objetivo)

        conteo = AutomataZombie.conteo_markov

        total = sum(conteo.values())

        partes = []

        for estado, veces in conteo.items():

            observada = (
                veces / total * 100
                if total > 0 else 0
            )

            partes.append(
                f"{estado} {observada:.0f}% "
                f"(π {ESTACIONARIA[estado] * 100:.0f}%)"
            )

        if self.viterbiInferencias != AutomataZombie.total_inferencias:

            self.viterbiResultado = AutomataZombie.precision_viterbi()

            self.viterbiInferencias = AutomataZombie.total_inferencias

        aciertosViterbi, totalViterbi = self.viterbiResultado

        precisionViterbi = (
            aciertosViterbi / totalViterbi * 100
            if totalViterbi > 0 else 0
        )

        precisionForward = (
            AutomataZombie.aciertos_forward
            / AutomataZombie.total_inferencias * 100
            if AutomataZombie.total_inferencias > 0 else 0
        )

        mejor = self.evolucion.mejor

        if mejor:

            genoma, fitnessMejor = mejor

            textoGenetico = (
                f"Genético gen {self.evolucion.generacion} "
                f"(n={self.evolucion.evaluados}): mejor "
                f"{fitnessMejor:.0f} | prom {self.evolucion.promedio:.0f}"
                f" | élite v{genoma['velocidad']:.2f} "
                f"esq {genoma['prob_esquivar'] * 100:.0f}% "
                f"reac {genoma['reaccion']:.0f} "
                f"evita {genoma['evitar_peligro'] * 100:.0f}%"
            )

        else:

            textoGenetico = (
                f"Genético gen {self.evolucion.generacion}: "
                f"esperando zombies evaluados..."
            )

        graficos.dibujar_panel_inferior([
            (
                textoGenetico,
                VERDE
            ),
            (
                f"HMM humor oculto: acierto forward "
                f"{precisionForward:.0f}% | viterbi "
                f"{precisionViterbi:.0f}%",
                MORADO
            ),
            (
                f"Markov tras ataque (n={total}): "
                + " | ".join(partes),
                CIAN
            ),
        ])

        if self.juegoTerminado:

            graficos.dibujar_final(self.victoria)

        pygame.display.flip()


    # EJECUTAR

    def ejecutar(self):

        ejecutando = True


        while ejecutando:

            dt = reloj.tick(FPS) / 1000


            ejecutando = self.eventos()


            self.actualizar(dt)


            self.dibujar()


        pygame.quit()