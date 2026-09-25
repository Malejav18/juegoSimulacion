import pygame

from config import (
    pantalla,
    reloj,
    FPS,
    ANCHO,
    CARRILES,
    fuente,
    fuenteGrande,
    BLANCO,
    NEGRO,
    VERDE,
    ROJO,
    AMARILLO
)

from personajes import (
    Jugador,
    Superviviente,
    Zombie
)

from automatas import AutomataZombie

from markov import crear_cadena_ataque


# Distribución estacionaria teórica
# de la cadena de ataque del zombie

ESTACIONARIA = (
    crear_cadena_ataque()
    .distribucion_estacionaria()
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

        # Reiniciar conteo de Markov

        for estado in AutomataZombie.conteo_markov:

            AutomataZombie.conteo_markov[estado] = 0


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

        # Si terminó, nada se mueve

        if self.juegoTerminado:

            return


        # CREAR ZOMBIES

        self.tiempoZombie += dt

        if self.tiempoZombie > 3:

            self.zombies.append(
                Zombie()
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
                dt
            )


        # BALAS

        self.actualizar_balas(dt)


        # ELIMINAR ZOMBIES

        for zombie in self.zombies[:]:

            if zombie.vida <= 0:

                self.zombies.remove(
                    zombie
                )

                self.eliminados += 1


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

        pantalla.fill(NEGRO)


        # CARRILES

        for y in CARRILES:

            pygame.draw.line(
                pantalla,
                BLANCO,
                (0, y + 40),
                (ANCHO, y + 40)
            )


        # JUGADOR

        self.jugador.dibujar()


        # SUPERVIVIENTES

        for superviviente in self.supervivientes:

            superviviente.dibujar()


        # ZOMBIES

        for zombie in self.zombies:

            zombie.dibujar()


        # BALAS

        for bala in self.balas:

            pygame.draw.circle(
                pantalla,
                AMARILLO,
                (
                    int(bala[0]),
                    CARRILES[bala[1]]
                ),
                5
            )


        # INFORMACIÓN

        texto = fuente.render(

            f"Zombies eliminados: "
            f"{self.eliminados}/"
            f"{self.objetivo}",

            True,
            BLANCO
        )

        pantalla.blit(
            texto,
            (15, 15)
        )


        controles = fuente.render(

            "W/S = cambiar carril | "
            "ESPACIO = disparar",

            True,
            BLANCO
        )

        pantalla.blit(
            controles,
            (500, 15)
        )


        # MARKOV: frecuencia observada vs teórica

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

        markovTexto = fuente.render(

            f"Markov tras ataque (n={total}): "
            + " | ".join(partes),

            True,
            BLANCO
        )

        pantalla.blit(
            markovTexto,
            (15, 470)
        )


        # FIN DEL JUEGO

        if self.juegoTerminado:

            if self.victoria:

                mensaje = "¡GANASTE!"

                color = VERDE

            else:

                mensaje = "PERDISTE"

                color = ROJO


            textoFinal = fuenteGrande.render(
                mensaje,
                True,
                color
            )

            pantalla.blit(
                textoFinal,
                (
                    ANCHO // 2
                    - textoFinal.get_width() // 2,

                    45
                )
            )


            reiniciar = fuente.render(

                "Juego detenido - "
                "Presiona R para reiniciar",

                True,
                BLANCO
            )

            pantalla.blit(
                reiniciar,
                (
                    ANCHO // 2
                    - reiniciar.get_width() // 2,

                    90
                )
            )


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