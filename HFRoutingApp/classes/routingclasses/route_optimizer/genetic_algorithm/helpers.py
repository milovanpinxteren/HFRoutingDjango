import math
import random

from HFRoutingApp.models import Spot, Geo, Hub, Operator
from django.core.exceptions import ObjectDoesNotExist
from math import radians, sin, cos, sqrt, atan2


class GeneticAlgorithmHelpers:
    def __init__(self, geos_to_spot, unchangeable_geos, operator_geo_dict, geo_coordinates, distance_matrix):
        self.geos_to_spot = geos_to_spot
        self.unchangeable_geos = unchangeable_geos
        self.operator_geo_dict = operator_geo_dict
        self.geo_coordinates = geo_coordinates
        self.distance_matrix = distance_matrix


    def initialize_population(self, routes, population_size):
        population = []
        for _ in range(population_size):
            individual = {}
            for driver, route in routes.items():
                fixed_stops_start = route[:2]
                fixed_stops_end = route[-2:]
                intermediate_stops = route[2:-2]
                random.shuffle(intermediate_stops)
                new_route = fixed_stops_start + intermediate_stops + fixed_stops_end
                individual[driver] = new_route
                population.append(individual)
        return population

    def find_furthest_geo(self, child): #returns geo of the stop which is furthest away from the other stops in all routes
        max_distance_to_stops = -1
        furthest_driver_id = None
        furthest_geo_id = None
        for driver_id, geo_ids in child.items():
            for index1, geo_id in enumerate(geo_ids): #each location
                total_distance_to_stops = 0 #The total distance from a location to every other location in the route
                if index1 >= 2 or index1 < len(geo_ids) - 2: #each other location
                    for index2, other_geo_id in enumerate(geo_ids):
                        if index2 >= 2 or index2 < len(geo_ids) - 2:
                            distance = self.distance_matrix[geo_id][other_geo_id]
                            total_distance_to_stops += distance
                            if total_distance_to_stops > max_distance_to_stops:
                                max_distance_to_stops = total_distance_to_stops
                                furthest_driver_id = driver_id
                                furthest_geo_id = geo_id
                                furthest_geo_index = index1
        return furthest_driver_id, furthest_geo_id, furthest_geo_index

    def find_middle_point(self, route):
        lat_sum, lon_sum = 0,0
        min_distance = float('inf')
        middle_geo_id = None

        for geo_id in route: #calculate the middle point of the route
            lat, lon = self.geo_coordinates[geo_id]
            lat_sum += lat
            lon_sum += lon
        centroid_lat, centroid_lon = (lat_sum / len(route)), (lon_sum / len(route))

        for geo_id in route: #check which geo is closest to the middle
            if geo_id not in route[:2] and geo_id not in route[-2:] and geo_id in self.unchangeable_geos:
                return geo_id #If the route has a mandatory location, use it as middle point
            else:
                lat, lon = self.geo_coordinates[geo_id]
                distance = math.sqrt((lat - centroid_lat) ** 2 + (lon - centroid_lon) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    middle_geo_id = geo_id

        return middle_geo_id

    def find_closest_geo(self, furthest_driver_id, geos_of_furtest, excluded_array): #excluded_array = current stops in route
        min_value = float("inf")
        min_key = None

        for key, value in geos_of_furtest.items():
            if key in excluded_array:
                continue  # If the key is already in the route
            closest_geo = key #If the key is not already in the route (potential swap)
            if closest_geo not in self.unchangeable_geos or closest_geo in self.operator_geo_dict.get(furthest_driver_id, []):
                if value < min_value:
                    min_value = value
                    min_key = key

        return min_key, min_value

    def mutate(self, child):
        try:
            swapped = False
            swapped_counter = 0
            furthest_driver_id, furthest_geo_id, furthest_geo_index = self.find_furthest_geo(child)
            middle_point = self.find_middle_point(child[furthest_driver_id])
            geos_of_furtest = self.distance_matrix[middle_point] #dict of all geo_ids: distances from the furthest geo
            closest_geo, min_value = self.find_closest_geo(furthest_driver_id, geos_of_furtest, child[furthest_driver_id])
            if min_value != float("inf"):
                while swapped == False:
                    for swap_driver_id, geo_ids in child.items():
                        for index, geo_id in enumerate(geo_ids):
                            if geo_id == closest_geo:
                                swapped_counter += 1
                                print(swapped_counter)
                                child[swap_driver_id][index] = furthest_geo_id
                                child[furthest_driver_id][furthest_geo_index] = closest_geo
                                swapped = True
                print('swapped')
                return child
            print('returning without swapping')
        except Exception as e:
            print('mutate exception: ', e)








    # def mutate(self, child):
    #     max_attempts = 5  # Add a limit to the number of attempts to prevent an infinite loop
    #     attempts = 0
    #     stop = None
    #
    #     while attempts < max_attempts and stop is None:
    #         attempts += 1
    #         driver1 = random.choice(list(child.keys()))
    #         stop1_index = random.randint(2, len(child[driver1]) - 3)
    #         driver2 = random.choice(list(child.keys()))
    #         stop2_index = random.randint(2, len(child[driver2]) - 3)
    #
    #         stop_candidate = child[driver1][stop1_index]
    #
    #         if stop_candidate not in self.unchangeable_geos or stop_candidate in self.operator_geo_dict[driver2]:
    #             stop = child[driver1].pop(stop1_index)
    #
    #         if stop:
    #             if child[driver2][stop2_index] not in self.unchangeable_geos or child[driver2][stop2_index] in self.operator_geo_dict[driver1]:
    #                 child[driver2].insert(stop2_index, stop)
    #             else:
    #                 child[driver1].insert(stop1_index, stop)
    #
    #     return child

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
