import random

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils


class GeneticAlgorithm:
    def __init__(self):
        self.route_utils = RouteUtils()
        self.population_size = 50
        self.generations = 50
        self.mutation_rate = 0.01
        self.distance_matrix = self.route_utils.get_distance_matrix()

    def initialize_population(self, routes):
        population = []
        for _ in range(self.population_size):
            chromosome = {}
            for operator, locations in routes.items():
                shuffled_locations = random.sample(locations, len(locations))
                chromosome[operator] = shuffled_locations
            population.append(chromosome)
        print('POPULATION,', population)
        return population

    def fitness(self, chromosome):
        total_distance = 0
        total_load = 0
        for i in range(len(chromosome) - 1):
            total_distance += self.distance_matrix[(chromosome[i].id, chromosome[i + 1].id)]
            total_load += self.location_crates[chromosome[i].id]
        if total_load > self.operator_capacity[1]:  # Assuming single operator for simplicity
            return float('inf')
        return total_distance

    def selection(self):
        ranked_population = sorted(self.population, key=self.fitness)
        return ranked_population[:self.population_size // 2]

    def crossover(self, parent1, parent2):
        child = parent1[:len(parent1) // 2] + [gene for gene in parent2 if gene not in parent1]
        return child

    def mutate(self, chromosome):
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(len(chromosome)), 2)
            chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
        return chromosome

    def evolve(self):
        new_population = []
        selected = self.selection()
        for _ in range(self.population_size):
            parent1, parent2 = random.sample(selected, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        self.population = new_population

    def do_evolution(self, routes):
        population = self.initialize_population(routes)
        for generation in range(self.generations):
            self.evolve()
        pass
