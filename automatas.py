from markov import crear_cadena_ataque, ESTADOS_ATAQUE


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

    # Decisión de Markov -> evento del autómata

    EVENTO_MARKOV = {
        "ESPERAR": "termina_ataque",
        "FRENESI": "frenesi",
        "RETROCEDER": "retrocede"
    }

    def __init__(self):

        self.estado = "VAGANDO"

        # Cada zombie tiene su propia
        # cadena de Markov

        self.cadena = crear_cadena_ataque()

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

        decision = self.cadena.siguiente()

        AutomataZombie.conteo_markov[decision] += 1

        self.cambiar_estado(
            self.EVENTO_MARKOV[decision]
        )

        return decision