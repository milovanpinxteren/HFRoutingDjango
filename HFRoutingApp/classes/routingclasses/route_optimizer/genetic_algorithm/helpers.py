import math
import random

from HFRoutingApp.models import Spot, Geo, Hub, Operator
from django.core.exceptions import ObjectDoesNotExist
import copy


class GeneticAlgorithmHelpers:
    def __init__(self, geos_to_spot, unchangeable_geos, operator_geo_dict, geo_coordinates, distance_matrix,
                 geo_avg_no_crates, vehicle_capacity):
        self.geo_avg_no_crates = geo_avg_no_crates
        self.vehicle_capacity = vehicle_capacity
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

    def find_furthest_geo(self, child):  # returns geo of the stop which is furthest from the other stops in all routes
        max_distance_to_stops = -1
        furthest_driver_id = None
        furthest_geo_id = None
        furthest_geo_index = None
        for driver_id, geo_ids in child.items():
            for index1, geo_id in enumerate(geo_ids):  # each location
                total_distance_to_stops = 0  # The total distance from a location to every other location in the route
                if index1 >= 2 or index1 < len(
                        geo_ids) - 2 and geo_id not in self.unchangeable_geos:  # each other location
                    for index2, other_geo_id in enumerate(geo_ids):
                        if index2 >= 2 or index2 < len(geo_ids) - 2:
                            try:
                                distance = self.distance_matrix[geo_id][other_geo_id]
                            except Exception as e:
                                print('error in distance_matrix')
                            total_distance_to_stops += distance
                            if total_distance_to_stops > max_distance_to_stops:
                                max_distance_to_stops = total_distance_to_stops
                                furthest_driver_id = driver_id
                                furthest_geo_id = geo_id
                                furthest_geo_index = index1
        if furthest_geo_index == None:
            print('error in find_furthest_geo')
        return furthest_driver_id, furthest_geo_id, furthest_geo_index

    def find_middle_point(self, route):
        lat_sum, lon_sum = 0, 0
        min_distance = float('inf')
        middle_geo_id = None

        for geo_id in route:  # calculate the middle point of the route
            lat, lon = self.geo_coordinates[geo_id]
            lat_sum += lat
            lon_sum += lon
        centroid_lat, centroid_lon = (lat_sum / len(route)), (lon_sum / len(route))

        for geo_id in route:  # check which geo is closest to the middle
            if geo_id not in route[:2] and geo_id not in route[-2:] and geo_id in self.unchangeable_geos:
                return geo_id  # If the route has a mandatory location, use it as middle point
            else:
                lat, lon = self.geo_coordinates[geo_id]
                distance = math.sqrt((lat - centroid_lat) ** 2 + (lon - centroid_lon) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    middle_geo_id = geo_id

        return middle_geo_id

    def find_closest_geo(self, furthest_driver_id, geos_of_furtest,
                         excluded_array):  # excluded_array = current stops in route
        min_value = float("inf")
        min_key = None

        for key, value in geos_of_furtest.items():
            if key in excluded_array:
                continue  # If the key is already in the route
            closest_geo = key  # If the key is not already in the route (potential swap)
            # If driver_id = 0, it only wants to find the closest geo and not swap the closest geo. Therefore the geo is allowed to be in unchangeable
            if closest_geo not in self.unchangeable_geos or closest_geo in self.operator_geo_dict.get(
                    furthest_driver_id, []) or furthest_driver_id == 0:
                if value < min_value:
                    min_value = value
                    min_key = key

        return min_key, min_value

    def mutate(self, child, mutation_type):
        if mutation_type == 'remove_furthest':
            child = self.remove_furthest_mutation(child)
        elif mutation_type == 'remove_high_capacities':
            child = self.remove_high_capacity_mutation(child)

        return child

    def remove_furthest_mutation(self, parent):
        child = {k: v[:] for k, v in parent.items()}
        # try:
        inserted = False
        driver_id_to_swap, geo_id_to_swap, geo_index_to_swap = self.find_furthest_geo(child)
        route_without_stop = copy.deepcopy(child[driver_id_to_swap])
        route_without_stop.remove(geo_id_to_swap)
        middle_point = self.find_middle_point(route_without_stop)
        dists_geo_to_swap = self.distance_matrix[middle_point]  # dict of all geo_ids: distances from the furthest geo
        closest_geo, min_value = self.find_closest_geo(driver_id_to_swap, dists_geo_to_swap,
                                                       child[driver_id_to_swap])  # The closest geo to the middle point

        # find closest geo to furthest_geo_id
        dists_geo_to_swap_with = self.distance_matrix[geo_id_to_swap]
        closest_geo_to_assign, min_value_to_assign = self.find_closest_geo(0, dists_geo_to_swap_with,
                                                                           child[driver_id_to_swap])
        # assign furthest_geo_id to route with closest geo
        if min_value != float("inf") and min_value_to_assign != float("inf"):
            child[driver_id_to_swap][geo_index_to_swap] = closest_geo

            for driver_id_to_assign, geo_ids in child.items():
                for geo_index_to_assign, geo_id in enumerate(geo_ids):
                    if geo_index_to_assign >= 2 or geo_index_to_assign < len(geo_ids) - 2:
                        if geo_id == closest_geo_to_assign:
                            if not inserted:
                                parent[driver_id_to_assign].insert(geo_index_to_assign, geo_id_to_swap)
                                try:
                                    parent[driver_id_to_swap].remove(geo_id_to_swap)
                                    inserted = True
                                except ValueError:
                                    print('valueerror')

                            elif inserted:
                                parent = self.routes_sorter(parent)
                                return parent

        else:
            print('No close stops found, not mutating')
        parent = self.routes_sorter(parent)
        return parent
        # except Exception as e:
        #     print('mutate exception: ', e)

    def remove_high_capacity_mutation(self, child):
        assignment_needed = []
        for operator, route in child.items():
            operator_capacity = self.vehicle_capacity[operator]
            total_route_load = 0
            for index in reversed(range(len(route))):
                if index > 2 and index < len(route) - 2:
                    geo_id = route[index]
                    total_route_load += self.geo_avg_no_crates[geo_id]
                    if total_route_load > operator_capacity:
                        # print('overload:', operator, route)
                        assignment_needed.append(geo_id)
                        route.pop(index)
                        total_route_load -= self.geo_avg_no_crates[geo_id]

        for geo_id in assignment_needed:
            inserted = False
            for operator, route in child.items():
                if not inserted:
                    operator_capacity = self.vehicle_capacity[operator]
                    total_route_load = sum(self.geo_avg_no_crates[existing_geo_id] for existing_geo_id in route)
                    if total_route_load + self.geo_avg_no_crates[geo_id] <= operator_capacity:
                        route.insert(3, geo_id) #insert it on the third spot (arbitrary)
                        total_route_load += self.geo_avg_no_crates[geo_id]
                        inserted = True
                        break


            if not inserted:
                print('failed to insert')


        return child

    def routes_sorter(self, routes):
        new_routes = {}
        for driver_id, geo_ids in routes.items():
            route = geo_ids[:2]
            remaining_geo_ids = geo_ids[2:-2]
            while remaining_geo_ids:
                last_geo_id = route[-1]
                nearest_neighbour = None
                nearest_distance = float('inf')

                for other_geo_id in remaining_geo_ids:
                    try:
                        distance = self.distance_matrix[last_geo_id][other_geo_id]
                        if 0 < distance < nearest_distance or other_geo_id == last_geo_id:
                            nearest_distance = distance
                            nearest_neighbour = other_geo_id
                    except Exception as e:
                        print('Sorting error', e)
                        nearest_neighbour = other_geo_id
                        #TODO: fix this

                if nearest_neighbour is not None:
                    route.append(nearest_neighbour)
                    remaining_geo_ids.remove(nearest_neighbour)

            route.extend(geo_ids[-2:])
            new_routes[driver_id] = route
        return new_routes

    def reverse_transform_routes(self, transformed_routes):
        routes_with_spots = {}
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
                except (IndexError, KeyError) as e:  # Could be a hub or driver
                    try:
                        instance = Hub.objects.get(geo__geo_id=geo_id)
                    except ObjectDoesNotExist:  # Is a driver
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

    def check_length_of_routes(self, parent1):
        removed = False
        drivers_to_remove = [driver for driver, route in parent1.items() if len(route) == 4]
        for driver in drivers_to_remove:
            # print(f'Removing driver {driver} with route of length 4')
            parent1.pop(driver)
            removed = True
        return removed, parent1
