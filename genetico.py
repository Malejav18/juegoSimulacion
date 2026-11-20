import random


GENES = {
    "velocidad": (0.7, 1.5),
    "prob_esquivar": (0.0, 1.0),
    "reaccion": (40.0, 260.0),
    "evitar_peligro": (0.0, 1.0),
}

TAMANO_POBLACION = 6

TAMANO_GENERACION = 3

TASA_MUTACION = 0.3

TAMANO_TORNEO = 2


def genoma_aleatorio():

    return {
        gen: random.uniform(minimo, maximo)
        for gen, (minimo, maximo) in GENES.items()
    }


def limitar(gen, valor):

    minimo, maximo = GENES[gen]

    return max(minimo, min(maximo, valor))


def calcular_fitness(zombie, escapo=False):

    fitness = (
        3 * zombie.danoInfligido
        + (750 - zombie.xMinimo) / 10
        + 4 * zombie.esquivas
    )

    if escapo:

        fitness += 50 + zombie.vida / 4

    return fitness


class AlgoritmoGenetico:

    def __init__(self):

        self.poblacion = []

        self.generacion = 1

        self.evaluados = 0

        self.pendientes = 0


    def nuevo_genoma(self):

        if len(self.poblacion) < 2:

            return genoma_aleatorio()

        padre = self.torneo()

        madre = self.torneo()

        return self.mutar(
            self.cruzar(padre, madre)
        )


    def torneo(self):

        candidatos = random.sample(
            self.poblacion,
            min(TAMANO_TORNEO, len(self.poblacion))
        )

        return max(candidatos, key=lambda individuo: individuo[1])[0]


    def cruzar(self, padre, madre):

        hijo = {}

        for gen in GENES:

            alfa = random.random()

            hijo[gen] = alfa * padre[gen] + (1 - alfa) * madre[gen]

        return hijo


    def mutar(self, genoma):

        for gen, (minimo, maximo) in GENES.items():

            if random.random() < TASA_MUTACION:

                genoma[gen] = limitar(
                    gen,
                    genoma[gen] + random.gauss(0, (maximo - minimo) * 0.15)
                )

        return genoma


    def evaluar(self, zombie, escapo=False):

        fitness = calcular_fitness(zombie, escapo)

        self.poblacion.append((zombie.genoma, fitness))

        self.evaluados += 1

        self.pendientes += 1

        if self.pendientes >= TAMANO_GENERACION:

            self.poblacion.sort(
                key=lambda individuo: individuo[1],
                reverse=True
            )

            del self.poblacion[TAMANO_POBLACION:]

            self.generacion += 1

            self.pendientes = 0

        return fitness


    @property
    def mejor(self):

        if not self.poblacion:

            return None

        return max(self.poblacion, key=lambda individuo: individuo[1])


    @property
    def promedio(self):

        if not self.poblacion:

            return 0

        return sum(f for _, f in self.poblacion) / len(self.poblacion)
