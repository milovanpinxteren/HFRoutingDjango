from django.db.models import Q

from HFRoutingApp.models import DistanceMatrix, OperatorLocationLink


class RouteUtils:
    def get_distance(self, origin, destination):
        try:
            distance_entry = DistanceMatrix.objects.get(Q(origin=origin) & Q(destination=destination))
            return distance_entry.distance_meters
        except DistanceMatrix.DoesNotExist:
            return float('inf')

    def get_nearest_location(self, current_location, locations):
        nearest_location = None
        shortest_distance = float('inf')
        for location in locations:
            distance = self.get_distance(current_location, location)
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_location = location
        return nearest_location

    def get_mandatory_groups(self, operators):
        """
        Gets the locations linked to an operator, these locations have to be in the same route (because same operator)
        Functions as a starting point for parallel insertion
        :return: dict with operator id as key and [location_ids] as value
        """
        mandatory_groups = {}
        for operator in operators:
            spot_ids = OperatorLocationLink.objects.filter(operator=operator).values_list('location__spot', flat=True)
            mandatory_groups[operator.id] = spot_ids
        return mandatory_groups

    def get_vehicle_capacities(self, operators):
        capacity_dict = {}
        for operator in operators:
            capacity_dict[operator.id] = operator.max_vehicle_load
        return capacity_dict
