import random


class ChildMaker:
    def __init__(self, geos_to_spot, unchangeable_spots):
        self.geos_to_spot = geos_to_spot
        self.unchangeable_spots = unchangeable_spots

    def crossover(self, parent1, parent2):
        child1 = {k: v[:] for k, v in parent1.items()}
        child2 = {k: v[:] for k, v in parent2.items()}

        stop1_changeable = False
        locations_tried_counter1 = 0
        while not stop1_changeable and locations_tried_counter1 < len(self.geos_to_spot):
            driver1 = random.choice(list(parent1.keys()))
            stop1_index = random.randint(2, len(parent1[driver1]) - 3)
            stop1 = parent1[driver1][stop1_index]
            if stop1 not in self.unchangeable_spots:
                stop1_changeable = True
            else:
                locations_tried_counter1 += 1


        stop2_changeable = False
        locations_tried_counter2 = 0
        while not stop2_changeable and locations_tried_counter2 < len(self.geos_to_spot):
            driver2 = random.choice(list(parent2.keys()))
            stop2_index = random.randint(2, len(parent2[driver2]) - 3)
            stop2 = parent2[driver2][stop2_index]
            if stop2 not in self.unchangeable_spots:
                stop2_changeable = True
            else:
                locations_tried_counter2 += 1

        if not stop1_changeable or not stop2_changeable:
            print('No changeable stops found, returning parents')
            return parent1, parent2

        for key, value_list in child1.items():
            if stop2 in value_list:
                child1[key][value_list.index(stop2)] = stop1

        for key, value_list in child2.items():
            if stop1 in value_list:
                child2[key][value_list.index(stop1)] = stop2

        if stop2 not in child1[driver1]:
            child1[driver1][stop1_index] = stop2
        else:
            # print('stop already present')
            child1[driver1][stop1_index] = stop1

        if stop1 not in child2[driver2]:
            child2[driver2][stop2_index] = stop1
        else:
            # print('stop already present')
            child2[driver2][stop2_index] = stop2

        return child1, child2