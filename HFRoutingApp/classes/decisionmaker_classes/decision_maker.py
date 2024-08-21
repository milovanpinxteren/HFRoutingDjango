from collections import defaultdict

from django.db.models import Count

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.models import Spot


class DecisionMaker:
    def __init__(self):
        self.route_utils = RouteUtils()
        self.distance_matrix = self.route_utils.get_distance_matrix_with_double_keys()

        self.profit_per_item = 1.15
        self.items_per_crate = 35
        self.gas_price = 2 #euro's per liter
        self.fuel_consumption = 0.07
        self.driver_wage = 20 #in euro
        self.average_speed = 50 #in km/h
        self.cost_per_km = (self.driver_wage / self.average_speed) + (self.gas_price * self.fuel_consumption)

    def make_decision(self, routes):
        items_per_stop = self.get_items_per_stop()
        stops_to_remove = []

        for operator, route in routes.items():
            route_distance = sum(self.distance_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))
            for index in range(2, len(route) - 2):  # Skip first 2 and last 2 stops
                current_distance = route_distance
                new_distance = (current_distance -
                                self.distance_matrix[route[index - 1]][route[index]] -
                                self.distance_matrix[route[index]][route[index + 1]] +
                                self.distance_matrix[route[index - 1]][route[index + 1]])
                distance_saving = (current_distance - new_distance) / 1000 #distance saved is stop is left out of route

                items_to_drop = items_per_stop[route[index]]
                stop_profit = items_to_drop * self.profit_per_item
                stop_cost = distance_saving * self.cost_per_km
                if stop_cost > stop_profit:
                    print('Advising to remove stop', route[index], ' from route ', operator, 'Would save ', stop_cost - stop_profit)
                    print(route)
                    # route.pop(index)
                    stops_to_remove.append((operator, index))
                elif stop_profit < stop_cost + 10:
                    print('Earning less than 10 euros on this stop', route[index], operator)
                    print(route)
                    # route.pop(index)
                    stops_to_remove.append((operator, index))

        for operator, index in sorted(stops_to_remove, key=lambda x: x[1], reverse=True):
            routes[operator].pop(index)



        return routes

    def get_items_per_stop(self):
        items_per_stop = defaultdict(float)
        spots = Spot.objects.select_related('location__geo').all()
        spot_counts = Spot.objects.values('location__geo').annotate(count=Count('id')).order_by()
        spot_counts_dict = {item['location__geo']: item['count'] for item in spot_counts}
        for spot in spots:
            geo_id = spot.location.geo.geo_id
            items_per_stop[geo_id] += (spot.avg_no_crates * self.items_per_crate or 0) / spot_counts_dict[geo_id]
        return items_per_stop
