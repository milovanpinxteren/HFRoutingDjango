import random


class GeneticAlgorithmHelpers:
    def initialize_population(self, routes, population_size):
        population = []
        for _ in range(population_size):
            chromosome = {}
            for operator, locations in routes.items():
                preserved_locations = locations[:2] + locations[-2:]  # Preserve the first and last 2 locations
                middle_locations = random.sample(locations[2:-2], len(locations) - 4)
                # Combine the preserved, shuffled middle, and last locations to form the chromosome
                chromosome[operator] = preserved_locations[:2] + middle_locations + preserved_locations[-2:]
            population.append(chromosome)
        return population

    def mutate(self, chromosome, mutation_rate):
        for vehicle in chromosome:
            if random.random() < mutation_rate:
                idx1, idx2 = random.sample(range(len(chromosome[vehicle])), 2)
                chromosome[vehicle][idx1], chromosome[vehicle][idx2] = chromosome[vehicle][idx2], chromosome[vehicle][
                    idx1]
        return chromosome

    def preserve_ends(self, route):
        return route[:2], route[-2:]

    def get_middle_segment(self, route):
        return route[2:-2]