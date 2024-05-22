from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils

"""
Takes routes as a dictionary (key = operator.id, value = [stops] and calculates cost per route.
return: dict with operator as key and cost per route as value and dict['total'] = total_costs
"""

class CalculateCostPerRoute:
    def __init__(self):
        self.route_utils = RouteUtils()

    def calculate_cost_per_route(self, routes):
        cost_per_route = {}
        total_costs = 0
        for operator_id, route in routes.items():
            route_costs = 0
            for index, stop in enumerate(route):
                if index < len(route) - 1:
                    next_stop = route[index + 1]
                    distance = self.route_utils.get_distance(stop, next_stop)
                    route_costs += distance
                    total_costs += route_costs
            cost_per_route[operator_id] = route_costs
        cost_per_route['total'] = total_costs
        return cost_per_route
