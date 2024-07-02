import random

from HFRoutingApp.models import Spot, Geo, Hub, Operator
from django.core.exceptions import ObjectDoesNotExist


class GeneticAlgorithmHelpers:
    def __init__(self, geos_to_spot, unchangeable_geos, operator_geo_dict):
        self.geos_to_spot = geos_to_spot
        self.unchangeable_geos = unchangeable_geos
        self.operator_geo_dict = operator_geo_dict

    def initialize_population(self, routes, population_size):
        population = []
        for _ in range(population_size):
            individual = {}
            for driver, route in routes.items():
                fixed_stops_start = route[:2]
                fixed_stops_end = route[-2:]
                # Intermediate stops that are not in the unchangeable_stops list
                # intermediate_stops = [stop for stop in route[2:-2] if stop not in self.unchangeable_geos]
                # unchangable_stops = [stop for stop in route[2:-2] if stop in self.unchangeable_geos]
                intermediate_stops = route[2:-2]

                random.shuffle(intermediate_stops)

                new_route = fixed_stops_start + intermediate_stops + fixed_stops_end
                individual[driver] = new_route
                population.append(individual)
        return population

    def mutate(self, child):
        max_attempts = 5  # Add a limit to the number of attempts to prevent an infinite loop
        attempts = 0
        stop = None

        while attempts < max_attempts and stop is None:
            attempts += 1
            driver1 = random.choice(list(child.keys()))
            stop1_index = random.randint(2, len(child[driver1]) - 3)
            driver2 = random.choice(list(child.keys()))
            stop2_index = random.randint(2, len(child[driver2]) - 3)

            stop_candidate = child[driver1][stop1_index]

            if stop_candidate not in self.unchangeable_geos or stop_candidate in self.operator_geo_dict[driver2]:
                stop = child[driver1].pop(stop1_index)

            if stop:
                if child[driver2][stop2_index] not in self.unchangeable_geos or child[driver2][stop2_index] in self.operator_geo_dict[driver1]:
                    child[driver2].insert(stop2_index, stop)
                else:
                    child[driver1].insert(stop1_index, stop)

        return child

    def reverse_transform_routes(self, transformed_routes):
        routes_with_spots = {}
        # print('GEOS TO SPOT')
        # print(self.geos_to_spot)
        for vehicle, geos in transformed_routes.items():
            routes_with_spots[vehicle] = []
            for geo_id in geos:
                try:
                    spot_ids = list(self.geos_to_spot[geo_id])
                    if len(spot_ids) > 1:
                        spot_id = spot_ids.pop()
                    else:
                        spot_id = spot_ids[0]
                    instance = Spot.objects.get(id=spot_id)
                    self.geos_to_spot[geo_id] = spot_ids
                except (IndexError, KeyError) as e: #Could be a hub or driver
                    # print('Error: ',e)
                    try:
                        instance = Hub.objects.get(geo__geo_id=geo_id)
                    except ObjectDoesNotExist: #Is a driver
                        try:
                            instance = Operator.objects.get(geo__geo_id=geo_id)
                        except ObjectDoesNotExist:
                            print('No spot, hub, operator found for: ', geo_id)
                except Exception as e:
                    print('Reverse transform route Exception: ', e)
                    instance = None
                if instance is not None:
                    routes_with_spots[vehicle].append(instance)
                elif instance is None:
                    print('could not convert geo to spot/hub/operator')

        return routes_with_spots
