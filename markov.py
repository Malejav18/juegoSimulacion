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
