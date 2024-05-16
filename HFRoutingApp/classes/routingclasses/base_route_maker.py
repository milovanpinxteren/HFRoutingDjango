from typing import List

from HFRoutingApp.models import CateringOrderLine, Location, Hub, OperatorLocationLink, Operator, Spot

"""
Makes the base routes based on parallel insertion. Takes mandatory stops in route and does a parallel insertion until
constraints are met, returns routes as map input
"""


class BaseRouteMaker:
    def make_base_routes(self):
        operators = Operator.objects.filter(active=True)
        spots = Spot.objects.filter(location__active=True).select_related('location')
        mandatory_groups = self.get_mandatory_groups(operators)
        for operator in operators:
            self.create_route_for_operator(operator, mandatory_groups[operator.id], spots)

        return

    def get_mandatory_groups(self, operators):
        """
        Gets the locations linked to an operator, these locations have to be in the same route (because same operator)
        Functions as a starting point for parallel insertion
        :return: dict with operator id as key and [location_ids] as value
        """
        mandatory_groups = {}
        for operator in operators:
            location_ids = OperatorLocationLink.objects.filter(operator=operator).values_list('location_id', flat=True)
            mandatory_groups[operator.id] = location_ids
        return mandatory_groups

    def create_route_for_operator(self, operator: Operator, mandatory_location_ids, spots):
        """
        Creates a route for a given operator starting with mandatory locations and then inserting
        other locations based on the lowest insertion cost (distance).
        """
        route_locations = [Location.objects.get(id=loc_id) for loc_id in mandatory_location_ids]
        other_locations = [spot.location for spot in spots if spot.location.id not in mandatory_location_ids]

        while other_locations:
            best_insertion_index, location_to_insert, best_cost = None, None, float('inf')

            for location in other_locations:
                cost = self.calculate_insertion_cost(route_locations, location)
                if cost < best_cost:
                    best_cost = cost
                    location_to_insert = location

            route_locations.append(location_to_insert)
            other_locations.remove(location_to_insert)

        print(route_locations)

    def calculate_insertion_cost(self, route_locations: List[Location], location_to_insert: Location) -> float:
        """
        Calculates the insertion cost based on the distance to the stop.

        :param route_locations: List of current locations in the route
        :param location_to_insert: The location to be inserted
        :return: The calculated insertion cost
        """
        if not route_locations:
            return 0  # If the route is empty, there's no cost

        last_location = route_locations[-1]
        last_geo = (last_location.geolocation.lat, last_location.geolocation.lon)
        insert_geo = (location_to_insert.geolocation.lat, location_to_insert.geolocation.lon)

        return geodesic(last_geo, insert_geo).kilometers
