import random
from collections import defaultdict

from django.db.models import Count

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.child_maker import ChildMaker
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.fitness_evaluator import FitnessEvaluator
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers
from HFRoutingApp.models import Spot, Operator, OperatorGeoLink, Geo, Location, Hub


class GeneticAlgorithm:
    def __init__(self):
        # Dict generators
        self.vehicle_capacity = {operator.id: operator.max_vehicle_load for operator in Operator.objects.all()}
        self.operator_geo_dict = defaultdict(list)
        operatorGeoLink_objects = OperatorGeoLink.objects.all()
        for obj in operatorGeoLink_objects:
            self.operator_geo_dict[obj.operator.id].append(obj.geo.geo_id)

        self.geos_to_spot = {}
        for spot in Spot.objects.select_related('location__geo').all():
            geo_id = spot.location.geo_id
            self.geos_to_spot.setdefault(geo_id, []).append(spot.id)
        # self.unchangeable_geos = [link.geo_id for link in OperatorGeoLink.objects.all()]
        self.unchangeable_geos = [link.geo_id for link in OperatorGeoLink.objects.all()] + \
                                 [hub.geo_id for hub in Hub.objects.all()] + \
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
        self.population_size = 40
        self.generations = 300  # 1300
        # self.mutation_rate = 1  # 0.2
        # self.crossover_rate = 0.5
        self.elitism_count = 8
        self.tournament_size = 8
        self.travel_time_exceeded_penalty = 4000
        self.infeasible_childs_counter = 0
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
        selected = []
        for _ in range(2):  # Select two parents
            tournament = random.sample(self.ranked_population, self.tournament_size)
            parent = min(tournament, key=self.fitness_evaluator.fitness)
            selected.append(parent)
        return selected[0], selected[1]

    def evolve(self):
        self.ranked_population = sorted(self.population, key=self.fitness_evaluator.fitness)
        self.elites = self.ranked_population[:self.elitism_count]
        self.total_ranks = sum(range(1, len(self.ranked_population) - self.elitism_count + 1))
        self.selection_probabilities = [(i + 1) / self.total_ranks for i in
                                        range(len(self.ranked_population) - self.elitism_count)]
        new_population = []
        self.mutation_type = 'remove_high_capacities'
        if self.infeasible_childs_counter < (self.population_size / 3):
            self.mutation_type = 'remove_furthest'
        else:
            self.mutation_type = 'remove_high_capacities'
        self.infeasible_childs_counter = 0
        new_population.extend(self.elites)
        while len(new_population) < self.population_size:
            parent1, parent2 = self.tournament_selection()
            # self.mutation_type = 'remove_high_capacities'
            parent_fitness = self.fitness_evaluator.fitness(parent1)
            # if parent_fitness == float("inf"):
            #     mutation_counter = 0
            #     child1 = self.ga_helpers.mutate(parent1, self.mutation_type)
            #     child_fitness = self.fitness_evaluator.fitness(child1)
            #     while child_fitness == float("inf"):
            #         child1 = self.ga_helpers.mutate(child1, self.mutation_type)
            #         child_fitness = self.fitness_evaluator.fitness(child1)
            #         mutation_counter += 1
            #         print("child fitness after mutation", mutation_counter, 'is ', child_fitness)
            # else:
            child1 = self.ga_helpers.mutate(parent1, self.mutation_type)
            child_fitness = self.fitness_evaluator.fitness(child1)
            print("child fitness", child_fitness)
            # if child_fitness >= parent_fitness:
            print('mutation resulted in worse child, trying crossover')
            child1 = self.child_maker.crossover(parent1, 'remove_longest_detour')
            # child_fitness = self.fitness_evaluator.fitness(child1)
                # if child_fitness >= parent_fitness:
            print('first crossover resulted in worse child, trying second crossover')
            child1 = self.child_maker.crossover(child1, 'append_closest')
            child_fitness = self.fitness_evaluator.fitness(child1)
            # else:
            #     print(parent_fitness - child_fitness, ' improved')

            if child_fitness == float("inf"):
                self.infeasible_childs_counter += 1
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
        original_len = 0
        for operator, route in transformed_routes.items():
            original_len += len(route)
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
                print('New world record! Old: ', global_best_fitness, 'New: ', generational_best_fitness)
                print(generational_best)
                global_best = generational_best
                global_best_fitness = generational_best_fitness

        # best_solution = min(self.population, key=self.fitness_evaluator.fitness)
        print('COST PER GENERATION DICT')
        print(cost_per_generation_dict)
        routes_with_spots = self.ga_helpers.reverse_transform_routes(global_best)
        return routes_with_spots
