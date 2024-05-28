import random

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.models import Spot, Operator, Location


class GeneticAlgorithm:
    def __init__(self):
        self.route_utils = RouteUtils()
        self.population_size = 50
        self.generations = 50
        self.mutation_rate = 0.01
        self.distance_matrix = self.route_utils.get_distance_matrix()
        self.spot_crates = {spot.id: spot.avg_no_crates for spot in Spot.objects.all()}
        self.vehicle_capacity = {operator.id: operator.max_vehicle_load for operator in Operator.objects.all()}
        self.location_to_spot = {spot.location.id: spot.id for spot in Spot.objects.all()}

    def initialize_population(self, routes):
        self.population = []
        for _ in range(self.population_size):
            chromosome = {}
            for operator, locations in routes.items():
                shuffled_locations = random.sample(locations, len(locations))
                chromosome[operator] = shuffled_locations
            self.population.append(chromosome)
        print('POPULATION,', self.population)
        return self.population

    def fitness(self, chromosome):
        total_distance = 0
        for vehicle, route in chromosome.items():
            total_load = 0
            route_distance = 0
            for i in range(len(route)):
                if i < len(route) - 1:
                    try:
                        spot_id = self.location_to_spot[route[i]]
                        total_load += self.spot_crates[spot_id]
                    except KeyError:  # spot not found -> error or it is a driver
                        total_load += 0
                    route_distance += self.distance_matrix[(route[i], route[i + 1])]

            # if total_load > self.vehicle_capacity[vehicle]:

                # return float('inf')  # Penalize infeasible solutions
            total_distance += route_distance
        return total_distance

    def selection(self):
        ranked_population = sorted(self.population, key=self.fitness)
        return ranked_population[:self.population_size // 2]

    def crossover(self, parent1, parent2):
        child = {}
        for vehicle in parent1:
            midpoint = len(parent1[vehicle]) // 2
            child[vehicle] = parent1[vehicle][:midpoint] + [gene for gene in parent2[vehicle] if
                                                            gene not in parent1[vehicle][:midpoint]]
        return child

    def mutate(self, chromosome):
        for vehicle in chromosome:
            if random.random() < self.mutation_rate:
                idx1, idx2 = random.sample(range(len(chromosome[vehicle])), 2)
                chromosome[vehicle][idx1], chromosome[vehicle][idx2] = chromosome[vehicle][idx2], chromosome[vehicle][
                    idx1]
        return chromosome

    def evolve(self):
        new_population = []
        selected = self.selection()
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        self.population = new_population

    def do_evolution(self, routes):
        # transformed_routes = {}
        # for vehicle, locations in routes.items():
        #     transformed_routes[vehicle] = [getattr(loc, 'location', loc).id for loc in locations]
        transformed_routes = {vehicle: [getattr(loc, 'location', loc).id for loc in locations] for vehicle, locations in
                              routes.items()}

        self.initialize_population(transformed_routes)
        for generation in range(self.generations):
            self.evolve()
            best_fitness = self.fitness(self.population[0])
            print(f'Generation {generation}: Best Fitness = {best_fitness}')
        best_solution = min(self.population, key=self.fitness)
        routes_with_spots = self.reverse_transform_routes(best_solution)

        return routes_with_spots


    def reverse_transform_routes(self, transformed_routes):
        routes_with_spots = {}
        for vehicle, locations in transformed_routes.items():
            routes_with_spots[vehicle] = []
            for loc_id in locations:
                spot_id = self.location_to_spot.get(loc_id)
                if spot_id is not None:
                    spot_instance = Spot.objects.get(id=spot_id)
                    routes_with_spots[vehicle].append(spot_instance)
                else:
                    location_instance = Location.objects.get(id=loc_id)
                    routes_with_spots[vehicle].append(location_instance)
        return routes_with_spots