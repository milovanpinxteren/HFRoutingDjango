import math

"""
Euclidian distance for now. In future this will be calculated via Google Maps API, stored in DB and only updated
once a location is added or updated. (Or manual trigger)
"""
class DistanceMatrixMaker:
    def distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def calculate_distance_matrix(self, locations):
        num_locations = len(locations)
        distance_matrix = [[0] * num_locations for _ in range(num_locations)]
        for i in range(num_locations):
            for j in range(num_locations):
                distance_matrix[i][j] = self.distance(locations[i], locations[j])
        return distance_matrix