import random

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers
from HFRoutingApp.models import Spot, Operator, Location
from collections import Counter
import numpy as np


class GeneticAlgorithm:
    def __init__(self):
        self.route_utils = RouteUtils()
        self.population_size = 50
        self.generations = 50
        self.mutation_rate = 0.01
        self.distance_matrix = self.route_utils.get_distance_matrix()
        self.ga_helpers = GeneticAlgorithmHelpers()
        print('distance matrix got')
        self.spot_crates = {spot.id: spot.avg_no_crates for spot in Spot.objects.all()}
        self.vehicle_capacity = {operator.id: operator.max_vehicle_load for operator in Operator.objects.all()}
        self.location_to_spot = {spot.location.id: spot.id for spot in Spot.objects.all()}

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
        try:
            child = parent1.copy() #Copy parent, will be the child
            vehicle = random.choice(list(parent1.keys())) #Get a random route from parent1
            remaining_locations_parent1 = parent1[vehicle][2:-2] #Get the (non-preserved) locations of route
            child_locations_to_insert = remaining_locations_parent1.copy()
            random_parent1_index = random.randint(1, len(remaining_locations_parent1) - 1) #Get a random index
            old_value = remaining_locations_parent1[random_parent1_index] #The value of the random stop

            remaining_locations_parent2 = parent2[random.choice(list(parent2.keys()))][2:-2] #Get random loc from par2
            random_parent2_index = random.randint(1, len(remaining_locations_parent2) - 1) #Get index
            new_value = remaining_locations_parent2[random_parent2_index] #New random value
            print('OLD', vehicle, 'locs:', remaining_locations_parent1)
            if new_value not in child_locations_to_insert:
                child_locations_to_insert[random_parent1_index] = new_value #Replace old value with new
            else:
                print('ALREADY IN ROUTE')


            for key, value_list in child.items(): #Replace occurence of new value in child with old
                if new_value in value_list:
                    value_list[value_list.index(new_value)] = old_value
            print('NEW', vehicle, 'locs:', child_locations_to_insert)
            child_locations = child[vehicle][:2] + child_locations_to_insert + child[vehicle][-2:]
            child[vehicle] = child_locations
            return child
        except Exception as e:
            print(e)
            return parent1

    def evolve(self):
        new_population = []
        selected = self.selection()
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected, 2)
            child = self.crossover(parent1, parent2)
            # child = self.ga_helpers.mutate(child, self.mutation_rate)
            new_population.append(child)
        self.population = new_population

    def do_evolution(self, routes):
        transformed_routes = {vehicle: [getattr(loc, 'location', loc).id for loc in locations] for vehicle, locations in
                              routes.items()}
        print('transformed', transformed_routes)
        self.population = self.ga_helpers.initialize_population(transformed_routes, self.population_size)

        for generation in range(self.generations):
            self.evolve()
            best_fitness = self.fitness(self.population[0])
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
