import os
import django
import itertools
from statistics import mean


# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HFRoutingDjango.settings')
django.setup()

from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
# from HFRoutingApp.models import Spot, Operator, Location
# from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
# from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers

class HyperparameterTuner:
    def __init__(self, ga_class, hyperparameter_space, eval_function):
        self.ga_class = ga_class
        self.hyperparameter_space = hyperparameter_space
        self.eval_function = eval_function
        self.best_params = None
        self.best_score = float("inf")

    def grid_search(self):
        all_combinations = list(itertools.product(*self.hyperparameter_space.values()))
        print('all combs', all_combinations)
        for combination in all_combinations:
            params = dict(zip(self.hyperparameter_space.keys(), combination))
            score = self.eval_function(params)
            if score < self.best_score:
                self.best_score = score
                self.best_params = params
        return self.best_params, self.best_score


def evaluate_ga(params):
    ga = GeneticAlgorithm()
    ga.population_size = params['population_size']
    ga.generations = params['generations']
    ga.mutation_rate = params['mutation_rate']
    ga.elitism_count = params['elitism_count']
    ga.tournament_size = params['tournament_size']

    # Here you need to provide the appropriate routes data to the do_evolution method
    routes = {7: [328, 323, 267, 285, 280, 312, 268, 295, 275, 248, 282, 247, 323, 328], 9: [326, 323, 286, 271, 264, 254, 242, 320, 261, 265, 323, 326], 2: [290, 322, 263, 306, 306, 246, 315, 255, 301, 244, 273, 294, 309, 322, 290], 4: [331, 324, 276, 313, 310, 274, 317, 289, 245, 245, 279, 319, 324, 331], 6: [329, 322, 256, 260, 311, 281, 244, 243, 294, 269, 272, 308, 322, 329], 5: [330, 322, 246, 257, 311, 253, 288, 250, 252, 322, 330], 8: [327, 325, 287, 287, 298, 302, 302, 305, 270, 241, 243, 309, 283, 325, 327], 1: [290, 322, 315, 300, 301, 284, 288, 251, 250, 252, 322, 290]}
    best_solution = ga.do_evolution(routes)

    # Define how you want to measure the performance of the GA
    best_fitness = ga.fitness(best_solution)
    return best_fitness


# Define the hyperparameter space
hyperparameter_space = {
    'population_size': list(range(50, 250, 1)),
    'generations': list(range(500, 2500, 1)),
    'mutation_rate': [0 + 0.01 * i for i in range(int((0.4 - 0) / 0.01))],
    'elitism_count': list(range(1, 15, 1))
}

# Create the tuner and perform grid search
tuner = HyperparameterTuner(GeneticAlgorithm, hyperparameter_space, evaluate_ga)
best_params, best_score = tuner.grid_search()

print(f'Best Hyperparameters: {best_params}')
print(f'Best Score: {best_score}')
