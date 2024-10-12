from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.models import Hub, Operator, Spot

"""
Makes the base routes based on parallel insertion. Takes mandatory stops in route and does a parallel insertion until
constraints are met, returns routes as map input
"""


class MandatoryRouteMaker:
    def make_mandatory_routes(self, spots_to_route, date):
        self.route_utils = RouteUtils()
        if date:
            operators = Operator.objects.filter(active=True, operatorplanning__day=date)
        else:
            operators = Operator.objects.filter(active=True)
        self.hub_locations = [hub.geo for hub in Hub.objects.filter(active=True)]
        mandatory_groups = self.route_utils.get_mandatory_groups(operators)

        routed_locations = []
        mandatory_routes = {}
        assigned_geo_ids = set()

        for operator in operators:
            remaining_geos = [geo for geo in mandatory_groups[operator.id] if geo not in assigned_geo_ids]
            mandatory_groups[operator.id] = remaining_geos
            mandatory_route = self.create_mandatory_route(operator, mandatory_groups[operator.id])
            routed_locations.extend(mandatory_route)
            for geo in mandatory_route[2:-2]:
                assigned_geo_ids.add(geo.geo_id)
            mandatory_routes[operator.id] = mandatory_route

        if spots_to_route:
            print('Spots to route: ', spots_to_route)
            remaining_spots = Spot.objects.filter(id__in=spots_to_route['stops'].keys(), active=True).exclude(
                location__geo__in=routed_locations).select_related('location__geo')
        else:
            remaining_spots = Spot.objects.filter(active=True).exclude(
                location__geo__in=routed_locations).select_related('location__geo')

        return mandatory_routes, remaining_spots, operators

    def create_mandatory_route(self, operator, mandatory_geos):
        # spots = Spot.objects.filter(id__in=mandatory_spots)
        spots = Spot.objects.filter(location__geo__geo_id__in=mandatory_geos)
        current_location = operator.geo
        route = [current_location]
        closest_hub = self.route_utils.get_nearest_location(current_location, self.hub_locations)
        route.append(closest_hub)
        current_location = closest_hub

        if spots:  # If there is a mandatory driver-location assignment
            spots_list = [spot.location.geo for spot in spots]
            while spots_list:
                closest_spot = self.route_utils.get_nearest_location(current_location, spots_list)
                route.append(closest_spot)
                spots_list.remove(closest_spot)
                current_location = closest_spot

        route.append(closest_hub)
        route.append(operator.geo)
        return route
