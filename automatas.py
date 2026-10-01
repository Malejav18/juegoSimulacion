from markov import crear_hmm_zombie, ESTADOS_ATAQUE


# AUTÓMATA DEL SUPERVIVIENTE

class AutomataSuperviviente:

    def __init__(self):

        self.estado = "CAMINAR"

        self.estados = {

            "CAMINAR": {
                "detecta_zombie": "HUYENDO",
                "no_hay_zombie": "CAMINAR"
            },

            "HUYENDO": {
                "logra_huir": "A_SALVO",
                "es_atacado": "HERIDO"
            },

            "HERIDO": {
                "recupera": "A_SALVO"
            },

            "A_SALVO": {
                "no_hay_zombie": "CAMINAR"
            }
        }

    def cambiar_estado(self, evento):

        if evento in self.estados[self.estado]:

            self.estado = (
                self.estados[self.estado][evento]
            )


# AUTÓMATA DEL ZOMBIE

class AutomataZombie:

    # Veces que cada decisión de Markov
    # ocurrió en la partida (todos los zombies)

    conteo_markov = {estado: 0 for estado in ESTADOS_ATAQUE}

    historiales = []

    aciertos_forward = 0

    total_inferencias = 0

    # Decisión de Markov -> evento del autómata

    EVENTO_MARKOV = {
        "ESPERAR": "termina_ataque",
        "FRENESI": "frenesi",
        "RETROCEDER": "retrocede"
    }

    def __init__(self):

        self.estado = "VAGANDO"

        self.hmm = crear_hmm_zombie()

        self.observaciones = []

        self.ocultos = []

        self.creencia = None

        AutomataZombie.historiales.append(self)

        self.estados = {

            "VAGANDO": {
                "detecta_jugador": "LLEGANDO",
                "sin_jugador": "VAGANDO"
            },

            "LLEGANDO": {
                "llega_objetivo": "ATACANDO"
            },

            "ATACANDO": {
                "termina_ataque": "ESPERANDO",
                "frenesi": "ATACANDO",
                "retrocede": "RETROCEDIENDO"
            },

            "ESPERANDO": {
                "turno_disponible": "LLEGANDO"
            },

            "RETROCEDIENDO": {
                "termina_retroceso": "LLEGANDO"
            }
        }

    def cambiar_estado(self, evento):

        if evento in self.estados[self.estado]:

            self.estado = (
                self.estados[self.estado][evento]
            )


    # Al terminar un ataque la cadena de
    # Markov decide qué evento ocurre

    def terminar_ataque(self):

        oculto, decision = self.hmm.paso()

        self.ocultos.append(oculto)

        self.observaciones.append(decision)

        self.creencia = self.hmm.filtrar(
            self.creencia,
            decision
        )

        AutomataZombie.total_inferencias += 1

        if self.estimacion == oculto:

            AutomataZombie.aciertos_forward += 1

        AutomataZombie.conteo_markov[decision] += 1

        self.cambiar_estado(
            self.EVENTO_MARKOV[decision]
        )

        return decision


    @property
    def creencia_actual(self):

        if self.creencia is None:

            return self.hmm.forward([])

        return self.creencia


    @property
    def estimacion(self):

        creencia = self.creencia_actual

        return max(creencia, key=creencia.get)


    @classmethod
    def precision_viterbi(cls):

        aciertos = 0

        total = 0

        for automata in cls.historiales:

            decodificados = automata.hmm.viterbi(
                automata.observaciones
            )

            for real, estimado in zip(automata.ocultos, decodificados):

                total += 1

                if real == estimado:

                    aciertos += 1

        return aciertos, total


    @classmethod
    def reiniciar_estadisticas(cls):

        for estado in cls.conteo_markov:

            cls.conteo_markov[estado] = 0

        cls.historiales.clear()

        cls.aciertos_forward = 0

        cls.total_inferencias = 0