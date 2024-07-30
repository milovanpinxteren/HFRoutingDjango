"""
Evaluates the fitness of a solution.
Currently based on:
    - Minimizing distance
    - Hard constraints: vehicle capacity and location opening time
    - Soft constraint: travel time longer than 6 hours (risk of being late at a location)

"""
from datetime import datetime, timedelta


# TODO implement: soft constraint: Total travel time + total fill time + total walk time < 6 hours
# TODO implement: hard constraint: arrival time should not be prior to opening time of location

class FitnessEvaluator:
    def __init__(self, geo_avg_no_crates, distance_matrix, vehicle_capacity, starting_times_dict,
                 geo_avg_fill_times, location_opening_times, travel_time_exceeded_penalty):
        self.geo_avg_no_crates = geo_avg_no_crates
        self.distance_matrix = distance_matrix
        self.vehicle_capacity = vehicle_capacity
        self.starting_times_dict = starting_times_dict
        self.geo_avg_fill_times = geo_avg_fill_times
        self.location_opening_times = location_opening_times
        self.travel_time_exceeded_penalty = travel_time_exceeded_penalty

    def fitness(self, chromosome):
        try:
            total_penalty = 0
            for vehicle, route in chromosome.items():
                total_load = 0
                route_travel_time = 0
                for i in range(len(route)-1):
                    geo_id = route[i]
                    next_geo_id = route[i + 1]
                    if i > 2 and i < len(route) - 2:
                        total_load += self.geo_avg_no_crates[geo_id]
                    try:
                        if total_load <= self.vehicle_capacity[vehicle]:
                            route_travel_time += self.calculate_travel_time(geo_id, next_geo_id)
                            time_constraint_met = self.check_time_constraint(vehicle, geo_id, route_travel_time)
                            if time_constraint_met:
                                if route_travel_time >= 360 and i < len(route) - 2:  # If total of route (except for the last 2 stops is less than 6 hours
                                    total_penalty += self.travel_time_exceeded_penalty
                            elif not time_constraint_met: # if operator arrives at location before it is open.
                                print('Time constraints not met')
                                total_penalty = float("inf")
                        elif total_load > self.vehicle_capacity[vehicle]:
                            # print("CAP EXCEEDED PENALTY ", vehicle, route)
                            total_penalty = float("inf")
                    except KeyError:  # spot not found -> it is a driver/hub
                        total_load += 0
                total_penalty += route_travel_time
            # print('total penalty: ', total_penalty)
            return total_penalty
        except Exception as e:
            print('Fitness exception: ', e)
            return float("inf")

    def calculate_travel_time(self, geo_id, next_geo_id):
        distance_increase = self.distance_matrix[geo_id][next_geo_id]
        try:
            time_to_add = self.geo_avg_fill_times[geo_id] + (
                        (distance_increase / 16.67) / 60)  # Assuming 60 km/h (16.67 m/s
        except Exception as e:
            print('Calculate travel time exception', e)
            time_to_add = (distance_increase / 16.67) / 60
        return time_to_add

    def check_time_constraint(self, vehicle, geo_id, route_travel_time):
        try:
            dummy_starting_date = datetime.combine(datetime.today(), self.starting_times_dict[vehicle])
            timestamp = (dummy_starting_date + timedelta(minutes=route_travel_time)).time()
            location_opening_time = self.location_opening_times[geo_id]
            if location_opening_time is None or location_opening_time <= timestamp:
                return True
            else:
                return False
        except KeyError: #Key not found -> It is the driver or hub
            return True
