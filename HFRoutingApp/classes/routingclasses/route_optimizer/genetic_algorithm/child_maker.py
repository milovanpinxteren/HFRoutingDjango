import random


class ChildMaker:
    def __init__(self, geos_to_spot, unchangeable_geos, operator_geo_dict, distance_matrix, geo_avg_no_crates):
        self.distance_matrix = distance_matrix
        self.geos_to_spot_len = len(geos_to_spot)
        self.unchangeable_geos = unchangeable_geos
        self.operator_geo_dict = operator_geo_dict
        self.geo_avg_no_crates = geo_avg_no_crates
        # self.vehicle_capacity = vehicle_capacity

    def crossover(self, parent1, parent2):
        child1 = self.append_closest_crossover(parent1, parent2)
        return child1

    def append_closest_crossover(self, parent1, parent2):
        child1 = {k: v[:] for k, v in parent1.items()}
        # child2 = {k: v[:] for k, v in parent2.items()}
        shortest_dist = float('inf')
        driver_id_to_append = None
        driver_id_to_remove = None
        stop_to_append = None
        stop_to_remove = None
        index_to_append = None
        index_to_remove = None

        for operator1, route1 in child1.items():
            for index1, stop1 in enumerate(route1):
                for operator2, route2 in child1.items():
                    for index2, stop2 in enumerate(route2):
                        if stop2 not in route1:
                            dist_to_stop = self.distance_matrix[stop1][stop2]
                            if dist_to_stop < shortest_dist and stop1 not in self.unchangeable_geos and stop2 not in self.unchangeable_geos:
                                shortest_dist = dist_to_stop
                                driver_id_to_append = operator1
                                driver_id_to_remove = operator2
                                stop_to_append = stop2
                                stop_to_remove = stop1
                                index_to_append = index1
                                index_to_remove = index2
        child1[driver_id_to_append][index_to_append] = stop_to_append
        child1[driver_id_to_remove][index_to_remove] = stop_to_remove

        return child1

    # def crossover(self, parent1, parent2):
    #     child1 = {k: v[:] for k, v in parent1.items()}
    #     child2 = {k: v[:] for k, v in parent2.items()}
    #
    #     stop1_changeable = False
    #     locations_tried_counter1 = 0
    #     while not stop1_changeable and locations_tried_counter1 < self.geos_to_spot_len:
    #         driver1 = random.choice(list(parent1.keys()))
    #         stop1_index = random.randint(2, len(parent1[driver1]) - 3)
    #         stop1 = parent1[driver1][stop1_index]
    #         if stop1 not in self.unchangeable_geos:
    #             stop1_changeable = True
    #         else:
    #             locations_tried_counter1 += 1
    #
    #
    #     stop2_changeable = False
    #     locations_tried_counter2 = 0
    #     while not stop2_changeable and locations_tried_counter2 < self.geos_to_spot_len:
    #         driver2 = random.choice(list(parent2.keys()))
    #         stop2_index = random.randint(2, len(parent2[driver2]) - 3)
    #         stop2 = parent2[driver2][stop2_index]
    #         if stop2 not in self.unchangeable_geos or stop2 in self.operator_geo_dict[driver1]:
    #             stop2_changeable = True
    #         else:
    #             locations_tried_counter2 += 1
    #
    #     if not stop1_changeable or not stop2_changeable:
    #         print('No changeable stops found, returning parents')
    #         return parent1, parent2
    #
    #     for key, value_list in child1.items():
    #         if stop2 in value_list:
    #             child1[key][value_list.index(stop2)] = stop1
    #
    #     for key, value_list in child2.items():
    #         if stop1 in value_list:
    #             child2[key][value_list.index(stop1)] = stop2
    #
    #     if stop2 not in child1[driver1]:
    #         child1[driver1][stop1_index] = stop2
    #     else:
    #         # print('stop already present')
    #         child1[driver1][stop1_index] = stop1
    #
    #     if stop1 not in child2[driver2]:
    #         child2[driver2][stop2_index] = stop1
    #     else:
    #         # print('stop already present')
    #         child2[driver2][stop2_index] = stop2
    #
    #     return child1, child2
