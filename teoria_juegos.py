import random


class JuegoEstrategico:
    """
    Juego simultáneo 2x2 entre un superviviente y un zombie.

    Superviviente:
        - DISPARAR
        - HUIR

    Zombie:
        - ATACAR
        - ESQUIVAR

    Los pagos cambian según el estado actual del juego:
        - vida del superviviente
        - vida del zombie
        - distancia entre ambos
        - creencia del HMM de que el zombie está FURIOSO

    Primero se buscan equilibrios de Nash en estrategias puras.
    Si no existe ninguno, se calcula el equilibrio mixto de un juego 2x2.
    """

    ESTRATEGIAS_SUPERVIVIENTE = (
        "DISPARAR",
        "HUIR"
    )

    ESTRATEGIAS_ZOMBIE = (
        "ATACAR",
        "ESQUIVAR"
    )

    def __init__(self, mostrar_decisiones=True):
        self.mostrar_decisiones = mostrar_decisiones


    @staticmethod
    def _limitar(valor, minimo=0.0, maximo=1.0):
        return max(minimo, min(maximo, valor))


    def construir_matrices(
        self,
        superviviente,
        zombie,
        distancia
    ):
        """
        Construye las matrices de utilidad para los dos jugadores.

        Las filas corresponden al superviviente:
            0 = DISPARAR
            1 = HUIR

        Las columnas corresponden al zombie:
            0 = ATACAR
            1 = ESQUIVAR
        """

        vida_superviviente = self._limitar(
            superviviente.vida / 50
        )

        vida_zombie = self._limitar(
            zombie.vida / 200
        )

        furia = self._limitar(
            zombie.automata.creencia_actual[
                "FURIOSO"
            ]
        )

        # 0 significa lejos y 1 significa muy cerca.
        proximidad = 1 - self._limitar(
            distancia / 200
        )

        # -------------------------------------------------
        # PAGOS DEL SUPERVIVIENTE
        # -------------------------------------------------
        #
        # Los pesos se calibraron para que la estrategia no
        # dependa casi exclusivamente del HMM. Ahora también
        # la distancia y la vida pueden cambiar la mejor
        # respuesta aunque P(FURIOSO) sea baja.

        # Si el zombie ATACA, disparar es atractivo cuando el
        # superviviente tiene buena vida, hay distancia y la
        # probabilidad de furia es baja. La proximidad penaliza
        # con fuerza esta estrategia porque disparar a muy corta
        # distancia implica exponerse al ataque.
        disparar_atacar = (
            4.2 * vida_superviviente
            + 1.8
            - 2.3 * furia
            - 3.8 * proximidad
        )

        # Si el zombie ESQUIVA, el disparo puede fallar, pero el
        # superviviente consigue romper momentáneamente su avance.
        # Es una situación favorable, aunque menos que acertar a un
        # zombie que sigue atacando desde una distancia segura.
        disparar_esquivar = (
            3.2
            + 0.7 * vida_superviviente
            + 0.7 * (1 - proximidad)
            - 0.5 * furia
        )

        # Huir frente a un ataque se vuelve atractivo cuando:
        # - el zombie está muy cerca,
        # - el HMM estima furia,
        # - o el superviviente tiene poca vida.
        huir_atacar = (
            1.7
            + 2.2 * furia
            + 2.8 * (1 - vida_superviviente)
            + 1.3 * proximidad
        )

        # Huir mientras el zombie esquiva también aporta seguridad,
        # pero desperdicia la oportunidad de disparar mientras el
        # zombie cambia de carril.
        huir_esquivar = (
            2.0
            + 1.5 * (1 - vida_superviviente)
            + 0.7 * furia
            + 0.4 * proximidad
        )

        pagos_superviviente = [
            [
                disparar_atacar,
                disparar_esquivar
            ],
            [
                huir_atacar,
                huir_esquivar
            ]
        ]

        # -------------------------------------------------
        # PAGOS DEL ZOMBIE
        # -------------------------------------------------

        # Atacar a alguien que dispara gana valor rápidamente
        # cuando el zombie está cerca o furioso. También es más
        # atractivo si conserva vida o el superviviente está
        # debilitado.
        atacar_disparo = (
            0.8
            + 3.0 * furia
            + 4.0 * proximidad
            + 1.4 * vida_zombie
            - 2.0 * vida_superviviente
        )

        # Esquivar un disparo es atractivo cuando todavía existe
        # distancia para cambiar de carril, el zombie no está muy
        # furioso o está herido. A corta distancia pierde utilidad:
        # allí suele ser mejor continuar el ataque.
        esquivar_disparo = (
            2.0
            + 1.4 * (1 - furia)
            + 1.5 * (1 - proximidad)
            + 0.7 * (1 - vida_zombie)
        )

        # Si el superviviente HUYÓ, atacar/perseguir es casi
        # siempre atractivo, especialmente a corta distancia.
        atacar_huida = (
            3.0
            + 2.0 * furia
            + 1.8 * proximidad
            + 1.0 * (1 - vida_superviviente)
        )

        # Si el superviviente ya está HUYENDO, esquivar no aporta
        # casi nada: no hay una línea de fuego que evitar. Por eso
        # esta utilidad se mantiene deliberadamente baja.
        esquivar_huida = (
            0.7
            + 0.6 * (1 - vida_zombie)
            + 0.2 * (1 - furia)
        )

        pagos_zombie = [
            [
                atacar_disparo,
                esquivar_disparo
            ],
            [
                atacar_huida,
                esquivar_huida
            ]
        ]

        contexto = {
            "vida_superviviente": vida_superviviente,
            "vida_zombie": vida_zombie,
            "furia": furia,
            "proximidad": proximidad
        }

        return (
            pagos_superviviente,
            pagos_zombie,
            contexto
        )


    @staticmethod
    def _equilibrios_puros(
        pagos_superviviente,
        pagos_zombie
    ):
        """
        Encuentra los equilibrios de Nash en estrategias puras.

        Una celda (i, j) es equilibrio si:
        - la fila i es mejor respuesta del superviviente
          ante la columna j;
        - la columna j es mejor respuesta del zombie
          ante la fila i.
        """

        equilibrios = []
        tolerancia = 1e-9

        for fila in range(2):

            for columna in range(2):

                mejor_superviviente = max(
                    pagos_superviviente[0][columna],
                    pagos_superviviente[1][columna]
                )

                mejor_zombie = max(
                    pagos_zombie[fila][0],
                    pagos_zombie[fila][1]
                )

                es_mejor_respuesta_superviviente = (
                    abs(
                        pagos_superviviente[fila][columna]
                        - mejor_superviviente
                    ) <= tolerancia
                )

                es_mejor_respuesta_zombie = (
                    abs(
                        pagos_zombie[fila][columna]
                        - mejor_zombie
                    ) <= tolerancia
                )

                if (
                    es_mejor_respuesta_superviviente
                    and es_mejor_respuesta_zombie
                ):
                    equilibrios.append(
                        (fila, columna)
                    )

        return equilibrios


    @staticmethod
    def _probabilidad_mixta_superviviente(
        pagos_zombie
    ):
        """
        Probabilidad p de que el superviviente use DISPARAR
        para dejar al zombie indiferente entre sus estrategias.
        """

        b11 = pagos_zombie[0][0]
        b12 = pagos_zombie[0][1]
        b21 = pagos_zombie[1][0]
        b22 = pagos_zombie[1][1]

        denominador = (
            b11 - b12 - b21 + b22
        )

        if abs(denominador) < 1e-9:
            return None

        p = (b22 - b21) / denominador

        if 0 <= p <= 1:
            return p

        return None


    @staticmethod
    def _probabilidad_mixta_zombie(
        pagos_superviviente
    ):
        """
        Probabilidad q de que el zombie use ATACAR
        para dejar al superviviente indiferente entre
        DISPARAR y HUIR.
        """

        a11 = pagos_superviviente[0][0]
        a12 = pagos_superviviente[0][1]
        a21 = pagos_superviviente[1][0]
        a22 = pagos_superviviente[1][1]

        denominador = (
            a11 - a12 - a21 + a22
        )

        if abs(denominador) < 1e-9:
            return None

        q = (a22 - a12) / denominador

        if 0 <= q <= 1:
            return q

        return None


    @staticmethod
    def _estrategia_segura(matriz, jugador_fila=True):
        """
        Respaldo para casos degenerados: usa maximin.
        """

        if jugador_fila:

            peores_resultados = [
                min(matriz[0]),
                min(matriz[1])
            ]

        else:

            peores_resultados = [
                min(matriz[0][0], matriz[1][0]),
                min(matriz[0][1], matriz[1][1])
            ]

        return max(
            range(2),
            key=lambda i: peores_resultados[i]
        )


    def decidir(
        self,
        superviviente,
        zombie,
        distancia
    ):

        (
            pagos_superviviente,
            pagos_zombie,
            contexto
        ) = self.construir_matrices(
            superviviente,
            zombie,
            distancia
        )

        equilibrios = self._equilibrios_puros(
            pagos_superviviente,
            pagos_zombie
        )

        prob_disparar = None
        prob_atacar = None

        if equilibrios:

            # Si hay más de un equilibrio puro, no imponemos
            # siempre el mismo: escogemos uno de ellos.
            fila, columna = random.choice(
                equilibrios
            )

            tipo = "NASH_PURO"

        else:

            prob_disparar = (
                self._probabilidad_mixta_superviviente(
                    pagos_zombie
                )
            )

            prob_atacar = (
                self._probabilidad_mixta_zombie(
                    pagos_superviviente
                )
            )

            if (
                prob_disparar is not None
                and prob_atacar is not None
            ):

                fila = (
                    0
                    if random.random() < prob_disparar
                    else 1
                )

                columna = (
                    0
                    if random.random() < prob_atacar
                    else 1
                )

                tipo = "NASH_MIXTO"

            else:

                fila = self._estrategia_segura(
                    pagos_superviviente,
                    jugador_fila=True
                )

                columna = self._estrategia_segura(
                    pagos_zombie,
                    jugador_fila=False
                )

                tipo = "MAXIMIN"

        estrategia_superviviente = (
            self.ESTRATEGIAS_SUPERVIVIENTE[fila]
        )

        estrategia_zombie = (
            self.ESTRATEGIAS_ZOMBIE[columna]
        )

        resultado = {
            "superviviente": estrategia_superviviente,
            "zombie": estrategia_zombie,
            "tipo": tipo,
            "pagos_superviviente": pagos_superviviente,
            "pagos_zombie": pagos_zombie,
            "prob_disparar": prob_disparar,
            "prob_atacar": prob_atacar,
            **contexto
        }

        if self.mostrar_decisiones:
            self._mostrar_resultado(
                resultado,
                distancia
            )

        return resultado


    @staticmethod
    def _mostrar_resultado(resultado, distancia):

        mensaje = (
            "[TEORIA DE JUEGOS] "
            f"distancia={distancia:.1f} | "
            f"P(FURIOSO)={resultado['furia']:.2f} | "
            f"{resultado['tipo']} -> "
            f"superviviente={resultado['superviviente']}, "
            f"zombie={resultado['zombie']}"
        )

        if resultado["tipo"] == "NASH_MIXTO":
            mensaje += (
                " | "
                f"P(DISPARAR)={resultado['prob_disparar']:.2f}, "
                f"P(ATACAR)={resultado['prob_atacar']:.2f}"
            )

        print(mensaje)


# Una sola instancia es suficiente para toda la partida.
juego_estrategico = JuegoEstrategico()


def decidir_enfrentamiento(
    superviviente,
    zombie,
    distancia
):
    return juego_estrategico.decidir(
        superviviente,
        zombie,
        distancia
    )
