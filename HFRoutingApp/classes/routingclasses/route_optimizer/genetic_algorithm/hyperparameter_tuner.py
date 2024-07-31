import os
import django
import itertools
from statistics import mean


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HFRoutingDjango.settings')
django.setup()

from HFRoutingApp.classes.routingclasses.helpers.calculate_cost_per_route import CalculateCostPerRoute
from HFRoutingApp.views.routing_views.calculate_routes_views import generate_start_route_for_tuner

# Configure Django settings


from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class HyperparameterTuner:
    def __init__(self, ga_class, hyperparameter_space):
        self.ga_class = ga_class
        self.hyperparameter_space = hyperparameter_space
        self.eval_function = evaluate_ga
        self.best_params = None
        self.best_score = float("inf")
        self.results = {}
        self.routes = self._initialize_routes('2024-06-19')

        print('ROUTES: ', self.routes)


    def _initialize_routes(self, date):
        self.routes = generate_start_route_for_tuner(date)
        # print('ROUTES: ', self.routes)
        return self.routes

    def grid_search(self):
        all_combinations = list(itertools.product(*self.hyperparameter_space.values()))
        print('no of combinations', len(all_combinations))
        counter = 0
        for combination in all_combinations:
            params = dict(zip(self.hyperparameter_space.keys(), combination))

            score = self.eval_function(params, self.routes)
            self.results[tuple(combination)] = score
            counter += 1
            print('PARAM RESULTS UNTIL NOW: ', self.results)
            print('AT ', counter, 'OUT OF ', len(all_combinations))
            if score < self.best_score:
                self.best_score = score
                self.best_params = params
        return self.best_params, self.best_score


def evaluate_ga(params, routes):
    ga = GeneticAlgorithm()
    cost_calculator = CalculateCostPerRoute()
    ga.population_size = params['population_size']
    ga.generations = params['generations']
    # ga.mutation_rate = params['mutation_rate']
    ga.elitism_count = params['elitism_count']
    ga.tournament_size = params['tournament_size']

    best_solution = ga.do_evolution(routes)

    # best_fitness = ga.fitness_evaluator.fitness(best_solution)
    best_fitness = cost_calculator.calculate_cost_per_route(best_solution)
    # print('best fitness', best_fitness)
    # print('best_fitness[total]', best_fitness['total'])
    return best_fitness['total']


# Define the hyperparameter space
hyperparameter_space = {
    'population_size': list(range(25, 126, 25)),
    'generations': list(range(50, 451, 100)),
    # 'mutation_rate': [0 + 0.05 * i for i in range(int((0.4 - 0) / 0.05))],
    'elitism_count': list(range(2, 14, 4)),
    'tournament_size': list(range(4, 14, 4))
}

# Create the tuner and perform grid search
tuner = HyperparameterTuner(GeneticAlgorithm, hyperparameter_space)
best_params, best_score = tuner.grid_search()

print(f'Best Hyperparameters: {best_params}')
print(f'Best Score: {best_score}')
