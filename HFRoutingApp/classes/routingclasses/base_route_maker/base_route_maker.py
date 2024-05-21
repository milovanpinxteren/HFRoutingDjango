from typing import List

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Sum

from HFRoutingApp.classes.routingclasses.base_route_maker.route_utils import RouteUtils
from HFRoutingApp.models import CateringOrderLine, Location, Hub, OperatorLocationLink, Operator, Spot, DistanceMatrix

"""
Makes the base routes based on parallel insertion. Takes mandatory stops in route and does a parallel insertion until
constraints are met, returns routes as map input
"""


class BaseRouteMaker:
    def make_base_routes(self):
        self.route_utils = RouteUtils()
        routed_locations = []
        operators = Operator.objects.filter(active=True)
        self.hub_locations = [hub.location for hub in Hub.objects.all()]
        spots = Spot.objects.filter(location__active=True).exclude(location__in=routed_locations).select_related('location')
        mandatory_groups = self.route_utils.get_mandatory_groups(operators)
        for operator in operators:
            base_route = self.create_base_route(operator, mandatory_groups[operator.id])
            routed_locations.extend(base_route)
            spots = Spot.objects.filter(location__active=True).exclude(location__in=routed_locations).select_related(
                'location')


        return

    def create_base_route(self, operator, mandatory_spots):
        spots = Spot.objects.filter(id__in=mandatory_spots)
        total_avg_crates = spots.aggregate(Sum('avg_no_crates'))['avg_no_crates__sum']
        print('route locations', spots)
        # print('Total average crates:', total_avg_crates)

        current_load = total_avg_crates
        current_location = operator.location
        route = [current_location]

        closest_hub = self.route_utils.get_nearest_location(current_location, self.hub_locations) #gets closest hub to driver
        route.append(closest_hub)
        current_location = closest_hub

        if spots:
            spots_list = [spot.location for spot in spots]
            while spots_list:
                print(spots_list)
                closest_spot = self.route_utils.get_nearest_location(current_location, spots_list)
                route.append(closest_spot)
                spots_list.remove(closest_spot)
                current_location = closest_spot
        else:
            print('No mandatory assignment known for operator')
        print('Route: ', route)
        route.append(closest_hub)
        route.append(current_location)
        return route
        # while route_locations:
        #     nearest_location, distance = self.route_utils.get_nearest_location(current_location, route_locations)
        #     if nearest_location:
        #         route.append(nearest_location)
        #         current_load += nearest_location.spot.avg_no_crates
        #         current_location = nearest_location
        #         route_locations.remove(nearest_location)
        #         if current_load > operator.max_vehicle_load:
        #             break
        #
        # return route






