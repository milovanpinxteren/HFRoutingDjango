from collections import defaultdict
import random

from django.db.models import Count

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.child_maker import ChildMaker
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.fitness_evaluator import FitnessEvaluator
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers
from HFRoutingApp.models import Spot, Operator, OperatorGeoLink, Geo, Location, Hub


class GeneticAlgorithm:
    def __init__(self):
        # Dict generators
        self.removed = False
        self.vehicle_capacity = {operator.id: operator.max_vehicle_load for operator in Operator.objects.all()}
        self.operator_geo_dict = defaultdict(list)
        operatorGeoLink_objects = OperatorGeoLink.objects.all()
        for obj in operatorGeoLink_objects:
            self.operator_geo_dict[obj.operator.id].append(obj.geo.geo_id)

        self.geos_to_spot = {}
        for spot in Spot.objects.select_related('location__geo').all():
            geo_id = spot.location.geo_id
            self.geos_to_spot.setdefault(geo_id, []).append(spot.id)
        self.unchangeable_geos = [link.geo_id for link in OperatorGeoLink.objects.all()] + \
                                 [hub.geo_id for hub in Hub.objects.all()] + \
                                 [operator.geo_id for operator in Operator.objects.all()]
        self.hubs_and_operators = [hub.geo_id for hub in Hub.objects.all()] + \
                                  [operator.geo_id for operator in Operator.objects.all()]
        self.location_opening_times = {location.geo_id: location.opening_time for location in Location.objects.all()}
        self.starting_times_dict = {operator.id: operator.starting_time for operator in Operator.objects.all()}
        spots = Spot.objects.select_related('location__geo').all()
        spot_counts = Spot.objects.values('location__geo').annotate(count=Count('id')).order_by()
        spot_counts_dict = {item['location__geo']: item['count'] for item in spot_counts}
        self.geo_avg_fill_times = defaultdict(float)
        self.geo_avg_no_crates = defaultdict(float)
        self.geo_coordinates = Geo.objects.all().values_list('geo_id', 'geolocation')

        geo_coordinates_with_lat_lng = {}
        for geo in self.geo_coordinates:
            geo_id, geolocation = geo
            geo_coordinates_with_lat_lng[geo_id] = (geolocation.lat, geolocation.lon)

        self.geo_coordinates = geo_coordinates_with_lat_lng
        for spot in spots:
            geo_id = spot.location.geo.geo_id
            self.geo_avg_fill_times[geo_id] += ((spot.fill_time_minutes or 0) + (spot.walking_time_minutes or 0)) / \
                                               spot_counts_dict[geo_id]
            self.geo_avg_no_crates[geo_id] += (spot.avg_no_crates or 0) / spot_counts_dict[geo_id]
        # Hyperparameters
        self.population_size = 60
        self.generations = 150  # 1300
        self.mutation_rate = 0.6
        # self.random_rate = 0.6
        self.crossover_type_choice = 0.5
        self.elitism_count = 4
        self.route_shuffle_amount = 15
        self.rebuilding_amount = 12
        self.acceptance_multiplier = 1.1
        self.tournament_size = 10
        self.travel_time_exceeded_penalty = 4000
        # Imports/inits
        self.route_utils = RouteUtils()
        self.distance_matrix = self.route_utils.get_distance_matrix_with_double_keys()
        self.ga_helpers = GeneticAlgorithmHelpers(self.geos_to_spot, self.unchangeable_geos, self.operator_geo_dict,
                                                  self.geo_coordinates, self.distance_matrix, self.geo_avg_no_crates,
                                                  self.vehicle_capacity)
        self.fitness_evaluator = FitnessEvaluator(self.geo_avg_no_crates, self.distance_matrix,
                                                  self.vehicle_capacity, self.starting_times_dict,
                                                  self.geo_avg_fill_times,
                                                  self.location_opening_times, self.travel_time_exceeded_penalty)
        self.child_maker = ChildMaker(self.geos_to_spot, self.unchangeable_geos, self.operator_geo_dict,
                                      self.distance_matrix, self.geo_avg_no_crates, self.vehicle_capacity,
                                      self.ga_helpers)

    def tournament_selection(self):
        try:
            # contestants = self.ranked_population[:self.tournament_size]
            contestants = random.sample(self.population, self.tournament_size)
            while len(contestants) > 1:
                contestant1, contestant2 = random.sample(contestants, 2)
                loser = max([contestant1, contestant2], key=self.fitness_evaluator.fitness)
                contestants.remove(loser)
            return contestants[0]
        except Exception as e:
            print(e)
            return self.ranked_population[0]

    def evolve(self):
        self.ranked_population = sorted(self.population, key=self.fitness_evaluator.fitness)
        self.elites = self.ranked_population[:self.elitism_count]
        self.total_ranks = sum(range(1, len(self.ranked_population) - self.elitism_count + 1))
        self.selection_probabilities = [(i + 1) / self.total_ranks for i in
                                        range(len(self.ranked_population) - self.elitism_count)]
        new_population = []
        new_population.extend(self.elites)
        while len(new_population) < self.population_size:
            self.mutation_type = 'remove_furthest'
            parent1 = self.tournament_selection()
            parent_fitness = self.fitness_evaluator.fitness(parent1)
            self.removed, parent1 = self.ga_helpers.check_length_of_routes(parent1)
            if parent_fitness == float("inf"):
                self.mutation_type = 'remove_high_capacities'
                print('remove high')
            random_number = random.random()
            if random_number <= self.mutation_rate:
                child1 = self.ga_helpers.mutate(parent1, self.mutation_type)
                mutation_check = self.check_geo_counts(child1)
                if mutation_check == False:
                    print('mutation failed', self.mutation_type)
            else:
                crossover_number = random.random()
                if crossover_number <= self.crossover_type_choice:
                    child1 = self.child_maker.crossover('remove_longest_detour', parent1)
                    remove_longest_detour = self.check_geo_counts(child1)
                    if remove_longest_detour == False:
                        print('remove_longest_detour failed')
                elif crossover_number > self.crossover_type_choice:
                    child1 = self.child_maker.crossover('append_closest', parent1)
                    append_closest = self.check_geo_counts(child1)
                    if append_closest == False:
                        print('append_closest failed')
            child_fitness = self.fitness_evaluator.fitness(child1)
            while child_fitness == float("inf"):
                child1 = self.ga_helpers.mutate(child1, 'remove_high_capacities')
                child_fitness = self.fitness_evaluator.fitness(child1)
                print('child was inf, now:', child_fitness)

            if child_fitness >= (parent_fitness * self.acceptance_multiplier): #accepting slightly worse solutions
                print('solution not better, shuffleing, parent - child', parent_fitness, child_fitness)
                i = 0
                while i < self.route_shuffle_amount:
                    child1 = self.child_maker.crossover('random_crossover', parent1)
                    random_crossover = self.check_geo_counts(child1)
                    if random_crossover == False:
                        print('random failed')
                    else:
                        i += 1
                i = 0
                shuffled_child_fitness = self.fitness_evaluator.fitness(child1)
                print('rebuilding, child fitness, shuffled_child_fitness', child_fitness, shuffled_child_fitness)
                if shuffled_child_fitness > (child_fitness * self.acceptance_multiplier):
                    while i < self.rebuilding_amount:
                        random_number = random.random()
                        if random_number <= self.mutation_rate:
                            child1 = self.ga_helpers.mutate(parent1, self.mutation_type)
                            mutation_check = self.check_geo_counts(child1)
                            if mutation_check == False:
                                print('mutation failed', self.mutation_type)
                        else:
                            crossover_number = random.random()
                            if crossover_number <= self.crossover_type_choice:
                                child1 = self.child_maker.crossover('remove_longest_detour', child1)
                                remove_longest_detour = self.check_geo_counts(child1)
                                if remove_longest_detour == False:
                                    print('remove_longest_detour failed')
                            elif crossover_number > self.crossover_type_choice:
                                child1 = self.child_maker.crossover('append_closest', child1)
                                append_closest = self.check_geo_counts(child1)
                                if append_closest == False:
                                    print('append_closest failed')
                        i += 1
                    child_fitness = self.fitness_evaluator.fitness(child1)
                    print('rebuild done, fitness:', child_fitness)
                    while child_fitness == float("inf"):
                        child1 = self.ga_helpers.mutate(child1, 'remove_high_capacities')
                        child_fitness = self.fitness_evaluator.fitness(child1)
                        print('child was inf, now:', child_fitness)

            new_population.extend([child1])
        self.population = new_population

    def do_evolution(self, routes):
        transformed_routes = {}
        for vehicle, stops in routes.items():
            vehicle_array = []
            for stop in stops:
                if isinstance(stop, Geo):
                    vehicle_array.append(stop.geo_id)
                elif isinstance(stop, Spot):
                    vehicle_array.append(stop.location.geo_id)
            transformed_routes[vehicle] = vehicle_array
        print('Begin routes:', transformed_routes)
        # original_len = 0
        self.geo_counts = {}
        for operator, route in transformed_routes.items():
            for stop in route:
                if stop in self.geo_counts:
                    self.geo_counts[stop] += 1
                else:
                    self.geo_counts[stop] = 1
        self.population = self.ga_helpers.initialize_population(transformed_routes, self.population_size)
        global_best = {}
        cost_per_generation_dict = {}
        global_best_fitness = float('inf')
        self.mutation_type = 'remove_furthest'
        self.crossover_type = 'append_closest'
        # self.crossover_type = 'remove_longest_detour'
        for generation in range(self.generations):
            self.evolve()
            generational_best = min(self.population, key=self.fitness_evaluator.fitness)
            generational_best_fitness = self.fitness_evaluator.fitness(generational_best)
            print(f'Generation {generation}: Best Fitness = {generational_best_fitness}')
            cost_per_generation_dict[generation] = generational_best_fitness
            if generational_best_fitness == float("inf"):
                self.mutation_type = 'remove_high_capacities'
            if generational_best_fitness < global_best_fitness:
                print('New record! Old: ', global_best_fitness, 'New: ', generational_best_fitness)
                print(generational_best)
                global_best = generational_best
                global_best_fitness = generational_best_fitness

        # best_solution = min(self.population, key=self.fitness_evaluator.fitness)
        print('best solution', global_best)
        print('COST PER GENERATION DICT')
        print(cost_per_generation_dict)
        routes_with_spots = self.ga_helpers.reverse_transform_routes(global_best)
        return routes_with_spots

    def check_geo_counts(self, child):
        try:
            new_geo_counts = {}
            for operator, route in child.items():
                for stop in route:
                    if stop in new_geo_counts:
                        new_geo_counts[stop] += 1
                    else:
                        new_geo_counts[stop] = 1

            for value, count in self.geo_counts.items():
                # if value in self.hubs_and_operators:
                #     print('Value is a hub or operator')
                if value not in self.hubs_and_operators:  # If a route is deleted, the geo_counts is not correct, but should continue
                    if new_geo_counts[value] != count:
                        return False
            return True



        except Exception as e:
            print('not good at all', e)
            print('self.geocounts', self.geo_counts)
            print('new_geo_counts', new_geo_counts)
            return False
