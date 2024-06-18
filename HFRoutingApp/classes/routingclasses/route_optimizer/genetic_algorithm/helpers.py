import random

from HFRoutingApp.models import Spot, Geo


class GeneticAlgorithmHelpers:
    def __init__(self, location_to_spot, unchangeable_spots):
        self.location_to_spot = location_to_spot
        self.unchangeable_spots = unchangeable_spots

    def initialize_population(self, routes, population_size):
        population = []
        for _ in range(population_size):
            individual = {}
            for driver, route in routes.items():
                fixed_stops_start = route[:2]
                fixed_stops_end = route[-2:]
                # Intermediate stops that are not in the unchangeable_stops list
                intermediate_stops = [stop for stop in route[2:-2] if stop not in self.unchangeable_spots]

                random.shuffle(intermediate_stops)

                new_route = fixed_stops_start + intermediate_stops + fixed_stops_end
                individual[driver] = new_route
                population.append(individual)
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
                    location_instance = Geo.objects.get(id=loc_id)
                    routes_with_spots[vehicle].append(location_instance)
        return routes_with_spots
