import math
import random


LAMBDA_INICIAL = 0.30

INCREMENTO_LAMBDA = 0.004

LAMBDA_MAXIMA = 0.55

DANO_MEDIA = 10

DANO_DESVIACION = 3

DANO_MINIMO = 2

DANO_MAXIMO = 20


class ProcesoPoisson:

    def __init__(
        self,
        lambda_inicial=LAMBDA_INICIAL,
        incremento=INCREMENTO_LAMBDA,
        lambda_maxima=LAMBDA_MAXIMA
    ):

        self.lambda_inicial = lambda_inicial

        self.incremento = incremento

        self.lambda_maxima = lambda_maxima

        self.tiempo = 0

        self.llegadas = 0

        self.candidatos = 0

        self.proxima = self.generar_llegada(0)


    def tasa(self, t):

        return min(
            self.lambda_maxima,
            self.lambda_inicial + self.incremento * t
        )


    def esperadas(self, t):

        t_tope = (
            (self.lambda_maxima - self.lambda_inicial) / self.incremento
        )

        if t <= t_tope:

            return self.lambda_inicial * t + self.incremento * t * t / 2

        return (
            self.lambda_inicial * t_tope
            + self.incremento * t_tope * t_tope / 2
            + self.lambda_maxima * (t - t_tope)
        )


    def generar_llegada(self, desde):

        t = desde

        while True:

            u = 1 - random.random()

            t += -math.log(u) / self.lambda_maxima

            self.candidatos += 1

            if random.random() <= self.tasa(t) / self.lambda_maxima:

                return t


    def actualizar(self, dt):

        self.tiempo += dt

        nuevas = 0

        while self.tiempo >= self.proxima:

            nuevas += 1

            self.llegadas += 1

            self.proxima = self.generar_llegada(self.proxima)

        return nuevas


    @property
    def aceptacion(self):

        if self.candidatos == 0:

            return 0

        return self.llegadas / self.candidatos


class DanoNormal:

    def __init__(
        self,
        media=DANO_MEDIA,
        desviacion=DANO_DESVIACION,
        minimo=DANO_MINIMO,
        maximo=DANO_MAXIMO
    ):

        self.media = media

        self.desviacion = desviacion

        self.minimo = minimo

        self.maximo = maximo

        self.muestras = 0

        self.suma = 0

        self.suma_cuadrados = 0


    def muestrear(self):

        while True:

            valor = random.gauss(self.media, self.desviacion)

            if self.minimo <= valor <= self.maximo:

                break

        valor = round(valor)

        self.muestras += 1

        self.suma += valor

        self.suma_cuadrados += valor * valor

        return valor


    @property
    def promedio(self):

        if self.muestras == 0:

            return 0

        return self.suma / self.muestras


    @property
    def desviacion_observada(self):

        if self.muestras < 2:

            return 0

        varianza = (
            self.suma_cuadrados - self.suma * self.suma / self.muestras
        ) / (self.muestras - 1)

        return math.sqrt(max(0, varianza))

    def reiniciar(self):

        self.muestras = 0

        self.suma = 0

        self.suma_cuadrados = 0


dano_zombie = DanoNormal()
