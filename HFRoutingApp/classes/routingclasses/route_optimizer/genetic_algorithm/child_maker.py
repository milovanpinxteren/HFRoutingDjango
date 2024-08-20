import random

from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.helpers import GeneticAlgorithmHelpers


class ChildMaker:
    def __init__(self, geos_to_spot, unchangeable_geos, operator_geo_dict, distance_matrix, geo_avg_no_crates,
                 vehicle_capacity, helpers, detour_cut_off_number):
        self.distance_matrix = distance_matrix
        self.geos_to_spot_len = len(geos_to_spot)
        self.unchangeable_geos = unchangeable_geos
        self.operator_geo_dict = operator_geo_dict
        self.geo_avg_no_crates = geo_avg_no_crates
        self.vehicle_capacity = vehicle_capacity
        self.helpers = helpers
        self.detour_cut_off_number = detour_cut_off_number

    def crossover(self, crossover_type, parent1):
        if crossover_type == 'append_closest':
            child1 = self.append_closest_crossover(parent1)
        elif crossover_type == 'remove_longest_detour':
            child1 = self.remove_longest_detour_crossover(parent1)
            i = 0
            while i < 3:
                child1 = self.remove_longest_detour_crossover(child1)
                i += 1
        elif crossover_type == 'random_crossover':
            child1 = self.random_crossover(parent1)
        return child1

    def remove_longest_detour_crossover(self, parent1):
        child1 = {k: v[:] for k, v in parent1.items()}
        child1 = self.helpers.routes_sorter(child1)
        detours = []
        for operator, route in child1.items():
            route_distance = sum(self.distance_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))
            for index in range(len(route) - 1):
                if index > 2 and index < len(route) - 2:
                    current_distance = route_distance
                    new_distance = (current_distance -
                                self.distance_matrix[route[index - 1]][route[index]] -
                                self.distance_matrix[route[index]][route[index + 1]] +
                                self.distance_matrix[route[index - 1]][route[index + 1]])
                    distance_saving = current_distance - new_distance
                    if route[index] not in self.unchangeable_geos:
                        detours.append((distance_saving, route[index], operator, index))

        detours.sort(reverse=True, key=lambda x: x[0])
        top_25_percent_index = max(1, len(detours) // self.detour_cut_off_number)
        top_detours = detours[:top_25_percent_index]
        selected_saving, stop_to_remove, operator_to_remove_from, index_to_remove = random.choice(top_detours)


        closest_distance = float("inf")
        operator_to_assign_to = None
        index_to_assign_to = None
        for operator, route in child1.items():
            for index in range(len(route) - 1):
                if index > 2 and index < len(route) - 2:
                    distance_to_stop = self.distance_matrix[route[index]][stop_to_remove]
                    if distance_to_stop < closest_distance and operator != operator_to_remove_from:
                        closest_distance = distance_to_stop
                        operator_to_assign_to = operator
                        index_to_assign_to = index

        if operator_to_remove_from and stop_to_remove and operator_to_assign_to and index_to_assign_to:
            child1[operator_to_remove_from].remove(stop_to_remove)
            child1[operator_to_assign_to].insert(index_to_assign_to + 1, stop_to_remove)
        else:
            print("error")

        return child1


    def append_closest_crossover(self, parent1):
        child1 = {k: v[:] for k, v in parent1.items()}
        shortest_dist = float('inf')
        driver_id_to_append = None
        driver_id_to_remove = None
        stop_to_append = None
        index_to_append = None

        for operator1, route1 in child1.items():
            for index1, stop1 in enumerate(route1[2:-2]):
                index1 += 2
                for operator2, route2 in child1.items():
                    if operator1 != operator2:
                        for index2, stop2 in enumerate(route2[2:-2]):
                            index2 += 2
                            if stop2 not in route1:
                                dist_to_stop = self.distance_matrix[stop1][stop2]
                                if (dist_to_stop < shortest_dist and
                                        stop1 not in self.unchangeable_geos and
                                        stop2 not in self.unchangeable_geos):
                                    operator_capacity = self.vehicle_capacity[operator1]
                                    current_capacity = sum(self.geo_avg_no_crates[stop] for stop in route1)
                                    new_capacity = current_capacity + self.geo_avg_no_crates[stop2]
                                    if new_capacity <= operator_capacity:
                                        shortest_dist = dist_to_stop
                                        driver_id_to_append = operator1
                                        driver_id_to_remove = operator2
                                        stop_to_append = stop2
                                        index_to_append = index1

        if stop_to_append is not None:
            child1[driver_id_to_append].insert(index_to_append + 1, stop_to_append)
            child1[driver_id_to_remove].remove(stop_to_append)
        else:
            print('No switch found')

        return child1

    def random_crossover(self, parent1):
        try:
            child1 = {k: v[:] for k, v in parent1.items()}

            stop1_changeable = False
            locations_tried_counter1 = 0
            while not stop1_changeable and locations_tried_counter1 < self.geos_to_spot_len:
                driver1 = random.choice(list(parent1.keys()))
                stop1_index = random.randint(2, len(parent1[driver1]) - 3)
                stop1 = parent1[driver1][stop1_index]
                if stop1 not in self.unchangeable_geos:
                    stop1_changeable = True
                else:
                    locations_tried_counter1 += 1

            stop2_changeable = False
            locations_tried_counter2 = 0
            while not stop2_changeable and locations_tried_counter2 < self.geos_to_spot_len:
                driver2 = random.choice(list(parent1.keys()))
                stop2_index = random.randint(2, len(parent1[driver2]) - 3)
                stop2 = parent1[driver2][stop2_index]
                if stop2 not in self.unchangeable_geos and driver1 != driver2:
                    stop2_changeable = True
                else:
                    locations_tried_counter2 += 1

            if not stop1_changeable or not stop2_changeable:
                print('No changeable stops found, returning parents')
                return parent1

            child1[driver1][stop1_index] = stop2
            child1[driver2][stop2_index] = stop1

            # for key, value_list in child1.items():
            #     if stop1 in value_list:
            #         child1[key][value_list.index(stop1)] = stop2
            #     elif stop2 in value_list:
            #         child1[key][value_list.index(stop2)] = stop1

        except Exception as e:
            print(e)

        return child1
