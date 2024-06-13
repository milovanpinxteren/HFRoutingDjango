from django.db.models import Q, Sum, FloatField
from django.db.models.functions import Coalesce

from HFRoutingApp.models import DistanceMatrix, OperatorLocationLink, Spot


class RouteUtils:
    def get_distance(self, origin, destination):
        try:
            if hasattr(origin, 'location'):
                origin = origin.location
            if hasattr(destination, 'location'):
                destination = destination.location
            distance = DistanceMatrix.objects.get(Q(origin=origin) & Q(destination=destination)).distance_meters
        except DistanceMatrix.DoesNotExist:
            distance = float('inf')
        return distance

    def get_distance_matrix(self):
        distance_matrix = {}
        distances = DistanceMatrix.objects.all()
        for distance in distances:
            key = (distance.origin.id, distance.destination.id)
            value = distance.distance_meters
            distance_matrix[key] = value
        return distance_matrix

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

    def update_capacities(self, routes, capacities):
        updated_capacities = {}
        for operator_id, route in routes.items():
            location_ids = [location.id for location in route]
            total_avg_no_crates = Spot.objects.filter(location_id__in=location_ids).aggregate(total=Coalesce(Sum('avg_no_crates'), 0, output_field=FloatField()))['total']
            updated_capacities[operator_id] = capacities[operator_id] - total_avg_no_crates
        return updated_capacities

