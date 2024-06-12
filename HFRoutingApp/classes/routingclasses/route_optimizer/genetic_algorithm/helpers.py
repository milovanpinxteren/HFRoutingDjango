import random

from HFRoutingApp.models import Spot, Location


class GeneticAlgorithmHelpers:
    def __init__(self, location_to_spot):
        self.location_to_spot = location_to_spot
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

    def mutate(self, child):
        driver1 = random.choice(list(child.keys()))
        stop1_index = random.randint(2, len(child[driver1]) - 3)
        stop = child[driver1].pop(stop1_index)

        driver2 = random.choice(list(child.keys()))
        stop2_index = random.randint(2, len(child[driver2]) - 3)
        child[driver2].insert(stop2_index, stop)
        return child


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