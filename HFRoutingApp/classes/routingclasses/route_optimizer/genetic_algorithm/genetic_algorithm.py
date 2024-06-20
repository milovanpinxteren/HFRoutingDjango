import random

from django.db.models import Sum, F

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.child_maker import ChildMaker
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.fitness_evaluator import FitnessEvaluator
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers
from HFRoutingApp.models import Spot, Operator, OperatorGeoLink, Geo, Location


class GeneticAlgorithm:
    def __init__(self):
        # Dict generators
        self.spot_crates = {spot.id: spot.avg_no_crates for spot in Spot.objects.all()}
        self.vehicle_capacity = {operator.id: operator.max_vehicle_load for operator in Operator.objects.all()}
        self.location_to_spot = {spot.location.id: spot.id for spot in Spot.objects.all()}
        self.unchangeable_spots = [link.location.id for link in OperatorGeoLink.objects.all()]
        self.location_opening_times = {location.id: location.opening_time for location in Location.objects.all()}
        self.starting_times_dict = {operator.id: operator.starting_time for operator in Operator.objects.all()}
        self.spot_fill_times = {spot['location']: spot['total_time'] for spot in Spot.objects.values('location')
                                .annotate(total_time=Sum(F('fill_time_minutes') + F('walking_time_minutes')))}
        # Hyperparameters
        self.population_size = 100
        self.generations = 25
        self.mutation_rate = 0.01
        self.elitism_count = 5
        self.tournament_size = 3
        self.travel_time_exceeded_penalty = 4000
        # Imports/inits
        self.route_utils = RouteUtils()
        self.distance_matrix = self.route_utils.get_distance_matrix()
        self.ga_helpers = GeneticAlgorithmHelpers(self.location_to_spot, self.unchangeable_spots)
        self.fitness_evaluator = FitnessEvaluator(self.location_to_spot, self.spot_crates, self.distance_matrix,
                                                  self.vehicle_capacity, self.starting_times_dict, self.spot_fill_times,
                                                  self.location_opening_times, self.travel_time_exceeded_penalty)
        self.child_maker = ChildMaker(self.location_to_spot, self.unchangeable_spots)

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
        new_population.extend(self.elites)
        while len(new_population) < self.population_size:
            parent1, parent2 = self.tournament_selection()
            try:
                child1, child2 = self.child_maker.crossover(parent1, parent2)
                if random.random() < self.mutation_rate:
                    child1 = self.ga_helpers.mutate(child1)
                    child2 = self.ga_helpers.mutate(child2)
            except Exception as e:
                print('Evolution error: ', e)
                child1, child2 = parent1, parent2

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
        global_best = {}
        global_best_fitness = float('inf')
        for generation in range(self.generations):
            self.evolve()
            print(min(self.population, key=self.fitness_evaluator.fitness))
            generational_best = min(self.population, key=self.fitness_evaluator.fitness)
            generational_best_fitness = self.fitness_evaluator.fitness(generational_best)
            print(f'Generation {generation}: Best Fitness = {generational_best_fitness}')
            if generational_best_fitness < global_best_fitness:
                print('New world record! Old: ', global_best_fitness, 'New: ', generational_best_fitness)
                global_best = generational_best
                global_best_fitness = generational_best_fitness

        # best_solution = min(self.population, key=self.fitness_evaluator.fitness)

        routes_with_spots = self.ga_helpers.reverse_transform_routes(global_best)
        return routes_with_spots
