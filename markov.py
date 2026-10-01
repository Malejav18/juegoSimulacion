import math
import random


# CADENA DE MARKOV
#
# P[i][j] = probabilidad de pasar
# del estado i al estado j.
# Cada fila debe sumar 1.
#
# Propiedad de Markov:
# P(X(n+1) = j | X(n) = i, X(n-1), ...)
#   = P(X(n+1) = j | X(n) = i)

class CadenaMarkov:

    def __init__(self, estados, matriz, estado_inicial):

        self.estados = estados

        self.matriz = matriz

        self.estado = estado_inicial

        # Validar que cada fila sume 1

        for i, fila in enumerate(matriz):

            if abs(sum(fila) - 1) > 1e-9:

                raise ValueError(
                    f"La fila {estados[i]} "
                    f"no suma 1: {sum(fila)}"
                )


    # SIGUIENTE ESTADO
    # Método de la transformada inversa:
    # se genera U ~ Uniforme(0, 1) y se
    # elige el primer estado cuya
    # probabilidad acumulada supere U.

    def siguiente(self):

        fila = self.matriz[
            self.estados.index(self.estado)
        ]

        u = random.random()

        acumulada = 0

        for estado, probabilidad in zip(self.estados, fila):

            acumulada += probabilidad

            if u < acumulada:

                self.estado = estado

                return estado

        # Por errores de redondeo
        self.estado = self.estados[-1]

        return self.estado


    # DISTRIBUCIÓN ESTACIONARIA
    # Se calcula pi = pi * P repitiendo
    # la multiplicación hasta converger.

    def distribucion_estacionaria(self, iteraciones=1000):

        n = len(self.estados)

        pi = [1 / n] * n

        for _ in range(iteraciones):

            pi = [
                sum(pi[i] * self.matriz[i][j] for i in range(n))
                for j in range(n)
            ]

        return dict(zip(self.estados, pi))


# CADENA DEL ZOMBIE AL TERMINAR UN ATAQUE
#
# ESPERAR    -> descansa antes de volver
# FRENESI    -> ataca otra vez de inmediato
# RETROCEDER -> se aleja y vuelve a acercarse

ESTADOS_ATAQUE = ["ESPERAR", "FRENESI", "RETROCEDER"]

MATRIZ_ATAQUE = [
    #  ESPERAR  FRENESI  RETROCEDER
    [0.50, 0.30, 0.20],   # desde ESPERAR
    [0.60, 0.25, 0.15],   # desde FRENESI (se cansa)
    [0.20, 0.70, 0.10],   # desde RETROCEDER (vuelve con furia)
]


def crear_cadena_ataque():

    return CadenaMarkov(
        ESTADOS_ATAQUE,
        MATRIZ_ATAQUE,
        "ESPERAR"
    )


def muestrear(valores, probabilidades):

    u = random.random()

    acumulada = 0

    for valor, probabilidad in zip(valores, probabilidades):

        acumulada += probabilidad

        if u < acumulada:

            return valor

    return valores[-1]


def log_seguro(p):

    return math.log(p) if p > 0 else float("-inf")


class ModeloOcultoMarkov:

    def __init__(
        self,
        estados,
        observaciones,
        matriz_a,
        matriz_b,
        pi_inicial
    ):

        self.estados = estados

        self.observaciones = observaciones

        self.matriz_a = matriz_a

        self.matriz_b = matriz_b

        self.pi_inicial = pi_inicial

        for i, fila in enumerate(matriz_b):

            if abs(sum(fila) - 1) > 1e-9:

                raise ValueError(
                    f"La emisión de {estados[i]} "
                    f"no suma 1: {sum(fila)}"
                )

        if abs(sum(pi_inicial) - 1) > 1e-9:

            raise ValueError(
                f"La distribución inicial "
                f"no suma 1: {sum(pi_inicial)}"
            )

        self.cadena = CadenaMarkov(
            estados,
            matriz_a,
            muestrear(estados, pi_inicial)
        )

        self.iniciado = False


    @property
    def oculto(self):

        return self.cadena.estado


    def paso(self):

        if self.iniciado:

            self.cadena.siguiente()

        self.iniciado = True

        fila = self.matriz_b[
            self.estados.index(self.oculto)
        ]

        observacion = muestrear(
            self.observaciones,
            fila
        )

        return self.oculto, observacion


    def filtrar(self, creencia, observacion):

        n = len(self.estados)

        k = self.observaciones.index(observacion)

        if creencia is None:

            previa = self.pi_inicial

        else:

            anterior = [creencia[e] for e in self.estados]

            previa = [
                sum(anterior[i] * self.matriz_a[i][j] for i in range(n))
                for j in range(n)
            ]

        alfa = [
            previa[j] * self.matriz_b[j][k]
            for j in range(n)
        ]

        total = sum(alfa)

        if total == 0:

            alfa = [1 / n] * n

        else:

            alfa = [a / total for a in alfa]

        return dict(zip(self.estados, alfa))


    def forward(self, secuencia):

        creencia = None

        for observacion in secuencia:

            creencia = self.filtrar(creencia, observacion)

        if creencia is None:

            return dict(zip(self.estados, self.pi_inicial))

        return creencia


    def viterbi(self, secuencia):

        if not secuencia:

            return []

        n = len(self.estados)

        log_a = [
            [log_seguro(p) for p in fila]
            for fila in self.matriz_a
        ]

        log_b = [
            [log_seguro(p) for p in fila]
            for fila in self.matriz_b
        ]

        k = self.observaciones.index(secuencia[0])

        delta = [
            log_seguro(self.pi_inicial[j]) + log_b[j][k]
            for j in range(n)
        ]

        rastros = []

        for observacion in secuencia[1:]:

            k = self.observaciones.index(observacion)

            nuevo = []

            rastro = []

            for j in range(n):

                mejor = max(
                    range(n),
                    key=lambda i: delta[i] + log_a[i][j]
                )

                nuevo.append(
                    delta[mejor] + log_a[mejor][j] + log_b[j][k]
                )

                rastro.append(mejor)

            delta = nuevo

            rastros.append(rastro)

        actual = max(range(n), key=lambda j: delta[j])

        camino = [actual]

        for rastro in reversed(rastros):

            actual = rastro[actual]

            camino.append(actual)

        camino.reverse()

        return [self.estados[i] for i in camino]


    def distribucion_observaciones(self):

        pi = self.cadena.distribucion_estacionaria()

        return {
            observacion: sum(
                pi[estado] * self.matriz_b[i][k]
                for i, estado in enumerate(self.estados)
            )
            for k, observacion in enumerate(self.observaciones)
        }


ESTADOS_OCULTOS = ["CALMADO", "HAMBRIENTO", "FURIOSO"]

MATRIZ_A = [
    [0.70, 0.20, 0.10],
    [0.15, 0.65, 0.20],
    [0.10, 0.25, 0.65],
]

MATRIZ_B = [
    [0.70, 0.10, 0.20],
    [0.30, 0.40, 0.30],
    [0.10, 0.75, 0.15],
]

PI_INICIAL = [0.60, 0.30, 0.10]


def crear_hmm_zombie():

    return ModeloOcultoMarkov(
        ESTADOS_OCULTOS,
        ESTADOS_ATAQUE,
        MATRIZ_A,
        MATRIZ_B,
        PI_INICIAL
    )


# PRUEBA SIN PYGAME
# python markov.py

if __name__ == "__main__":

    cadena = crear_cadena_ataque()

    print("Matriz de transición:")

    for estado, fila in zip(ESTADOS_ATAQUE, MATRIZ_ATAQUE):

        print(f"  {estado:<11} {fila}")


    print("\nDistribución estacionaria (teórica):")

    for estado, p in cadena.distribucion_estacionaria().items():

        print(f"  {estado:<11} {p:.4f}")


    pasos = 100000

    conteo = {estado: 0 for estado in ESTADOS_ATAQUE}

    for _ in range(pasos):

        conteo[cadena.siguiente()] += 1


    print(f"\nFrecuencia simulada ({pasos} pasos):")

    for estado, veces in conteo.items():

        print(f"  {estado:<11} {veces / pasos:.4f}")


    hmm = crear_hmm_zombie()

    pasos_hmm = 5000

    ocultos = []

    observaciones = []

    creencia = None

    aciertos_forward = 0

    for _ in range(pasos_hmm):

        oculto, observacion = hmm.paso()

        ocultos.append(oculto)

        observaciones.append(observacion)

        creencia = hmm.filtrar(creencia, observacion)

        if max(creencia, key=creencia.get) == oculto:

            aciertos_forward += 1

    decodificados = hmm.viterbi(observaciones)

    aciertos_viterbi = sum(
        1 for real, estimado in zip(ocultos, decodificados)
        if real == estimado
    )


    print(f"\nHMM del zombie ({pasos_hmm} pasos):")

    print("  Observaciones esperadas:")

    for observacion, p in hmm.distribucion_observaciones().items():

        print(f"    {observacion:<11} {p:.4f}")

    print(f"  Acierto forward: {aciertos_forward / pasos_hmm:.4f}")

    print(f"  Acierto viterbi: {aciertos_viterbi / pasos_hmm:.4f}")
