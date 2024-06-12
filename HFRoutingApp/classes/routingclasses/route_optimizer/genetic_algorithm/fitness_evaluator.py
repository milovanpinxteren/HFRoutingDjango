
class FitnessEvaluator:
    def __init__(self, location_to_spot, spot_crates, distance_matrix, vehicle_capacity):
        self.location_to_spot = location_to_spot
        self.spot_crates = spot_crates
        self.distance_matrix = distance_matrix
        self.vehicle_capacity = vehicle_capacity
    def fitness(self, chromosome):
        try:
            total_distance = 0
            for vehicle, route in chromosome.items():
                total_load = 0
                route_distance = 0
                for i in range(len(route)):
                    if i < len(route) - 1:
                        try:
                            spot_id = self.location_to_spot[route[i]]
                            total_load += self.spot_crates[spot_id]
                            # if total_load > self.vehicle_capacity[vehicle]:
                            #     total_distance += float("inf")
                        except KeyError:  # spot not found -> error or it is a driver
                            total_load += 0
                        route_distance += self.distance_matrix[(route[i], route[i + 1])]
                total_distance += route_distance
            return total_distance
        except Exception as e:
            print(e)
            return float("-inf")