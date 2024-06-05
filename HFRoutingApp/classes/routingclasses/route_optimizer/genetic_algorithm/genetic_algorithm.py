import random

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers
from HFRoutingApp.models import Spot, Operator, Location
from collections import Counter
import numpy as np
import timeit


class GeneticAlgorithm:
    def __init__(self):
        self.route_utils = RouteUtils()
        self.population_size = 100
        self.generations = 1
        self.mutation_rate = 0.01
        self.elitism_count = 5
        self.tournament_size = 3
        self.distance_matrix = self.route_utils.get_distance_matrix()
        self.ga_helpers = GeneticAlgorithmHelpers()
        print('distance matrix got')
        self.spot_crates = {spot.id: spot.avg_no_crates for spot in Spot.objects.all()}
        self.vehicle_capacity = {operator.id: operator.max_vehicle_load for operator in Operator.objects.all()}
        self.location_to_spot = {spot.location.id: spot.id for spot in Spot.objects.all()}

    def fitness(self, chromosome):
        try:
            total_distance = 0
            for vehicle, route in chromosome.items():
                total_load = 0
                route_distance = 0
                for i in range(len(route)):
                    if i < len(route) - 1:
                        try:
                            spot_id = self.location_to_spot[route[i]]
                            total_load += self.spot_crates[spot_id]
                            # if total_load > self.vehicle_capacity[vehicle]:
                            #     total_distance += float("inf")
                        except KeyError:  # spot not found -> error or it is a driver
                            total_load += 0
                        route_distance += self.distance_matrix[(route[i], route[i + 1])]
                total_distance += route_distance
            return total_distance
        except Exception as e:
            print(e)
            return float("-inf")

    def tournament_selection(self):
        selected = []
        for _ in range(2):  # Select two parents
            tournament = random.sample(self.ranked_population, self.tournament_size)
            parent = min(tournament, key=self.fitness)
            selected.append(parent)
        return selected[0], selected[1]

    def selection(self):
        # ranked_population = sorted(self.population, key=self.fitness, reverse=True)
        #
        # total_ranks = sum(range(1, len(ranked_population) + 1))
        # selection_probabilities = [(i + 1) / total_ranks for i in range(len(ranked_population))]
        # parent1 = random.choices(self.ranked_population[self.elitism_count:], weights=self.selection_probabilities, k=1)[0]
        # parent2 = random.choices(self.ranked_population[self.elitism_count:], weights=self.selection_probabilities, k=1)[0]
        # return parent1, parent2
        return self.ranked_population[0], self.ranked_population[1]
        # return ranked_population[:self.population_size // 2]

    def crossover(self, parent1, parent2):
        child1 = {k: v[:] for k, v in parent1.items()}
        child2 = {k: v[:] for k, v in parent2.items()}

        driver1 = random.choice(list(parent1.keys()))
        stop1_index = random.randint(2, len(parent1[driver1]) - 3)
        stop1 = parent1[driver1][stop1_index]

        driver2 = random.choice(list(parent2.keys()))
        stop2_index = random.randint(2, len(parent2[driver2]) - 3)
        stop2 = parent2[driver2][stop2_index]

        for key, value_list in child1.items():
            if stop2 in value_list:
                child1[key][value_list.index(stop2)] = stop1

        for key, value_list in child2.items():
            if stop1 in value_list:
                child2[key][value_list.index(stop1)] = stop2

        if stop2 not in child1[driver1]:
            child1[driver1][stop1_index] = stop2

        else:
            print('stop already present')
            child1[driver1][stop1_index] = stop1
        if stop1 not in child2[driver2]:
            child2[driver2][stop2_index] = stop1
        else:
            print('stop already present')
            child2[driver2][stop2_index] = stop2

        return child1, child2

    def evolve(self):
        self.ranked_population = sorted(self.population, key=self.fitness)
        self.elites = self.ranked_population[:self.elitism_count]
        self.total_ranks = sum(range(1, len(self.ranked_population) - self.elitism_count + 1))
        self.selection_probabilities = [(i + 1) / self.total_ranks for i in range(len(self.ranked_population) - self.elitism_count)]
        new_population = []
        new_population.extend(self.elites)
        while len(new_population) < self.population_size:
            # parent1, parent2 = self.selection()
            parent1, parent2 = self.tournament_selection()
            child1, child2 = self.crossover(parent1, parent2)
            if random.random() < self.mutation_rate:
                child1 = self.ga_helpers.mutate(child1)
                child2 = self.ga_helpers.mutate(child2)
            new_population.extend([child1, child2])
        self.population = new_population

    def do_evolution(self, routes):
        transformed_routes = {vehicle: [getattr(loc, 'location', loc).id for loc in locations] for vehicle, locations in
                              routes.items()}
        print('original')
        original_len = 0
        for operator, route in transformed_routes.items():
            print('route for ', operator, 'is length: ', len(route))
            original_len += len(route)
        print(original_len)
        print(transformed_routes)
        self.population = self.ga_helpers.initialize_population(transformed_routes, self.population_size)

        for generation in range(self.generations):
            self.evolve()
            best_fitness = self.fitness(self.population[0])
            print(min(self.population, key=self.fitness))
            print(f'Generation {generation}: Best Fitness = {best_fitness}')
        best_solution = min(self.population, key=self.fitness)
        routes_with_spots = self.reverse_transform_routes(best_solution)
        print(best_solution)
        print('len: ', len(best_solution))
        total_len = 0
        for operator, route in best_solution.items():
            print('route for ', operator, 'is length: ', len(route))
            total_len += len(route)
        print(total_len)
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
