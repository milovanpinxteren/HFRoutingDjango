from queue import PriorityQueue

from HFRoutingApp.classes.routingclasses.helpers.calculate_cost_per_route import CalculateCostPerRoute
from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from HFRoutingApp.models import Operator, Hub, Spot


class RouteExtender:
    def __init__(self):
        self.route_utils = RouteUtils()
        self.cost_calculator = CalculateCostPerRoute()
        self.genetic_algorithm = GeneticAlgorithm()

    def extend_route(self, routes, remaining_spots, operators):
        print('extending')
        queues = self.create_queues(operators, remaining_spots)
        capacities = self.route_utils.get_vehicle_capacities(operators)
        updated_capacities = self.route_utils.update_capacities(routes, capacities)
        print('inserting')
        inserted_routes = self.insert_spots(queues, routes, updated_capacities)
        print('to GA')
        print(inserted_routes)
        # return inserted_routes
        #TODO: Uncomment after Tuner is done

        optimized_routes = self.genetic_algorithm.do_evolution(inserted_routes)
        costs = self.cost_calculator.calculate_cost_per_route(optimized_routes)
        prepared_routes = self.prepare_routes_for_map(optimized_routes, costs)
        return prepared_routes

    def create_queues(self, operators, remaining_spots):
        """
        Creates Priority Queue for all operators with all remaining spots, based on distance from operator
        """
        queues = {operator: PriorityQueue() for operator in operators}
        queue_item_counter = 0
        for spot in remaining_spots:
            for operator in operators:
                cost = self.calculate_cost(spot, operator)
                queues[operator].put((cost, queue_item_counter, spot))
                queue_item_counter += 1
        return queues

    def calculate_cost(self, spot, operator):
        distance = self.route_utils.get_distance(spot.location.geo, operator.geo)
        return distance

    def insert_spots(self, queues, routes, capacities):
        operators_count = len(queues)
        operators_tried = 0
        while operators_tried < operators_count:
            for operator, queue in queues.items():
                if not queue.empty() and capacities[operator.id] > 0:
                    cost, _, spot = queue.get()
                    if capacities[operator.id] > (float(spot.avg_no_crates) if spot.avg_no_crates else 0):
                        routes[operator.id] = routes[operator.id][:-2] + [spot] + routes[operator.id][-2:]
                        capacities[operator.id] -= spot.avg_no_crates
                        self.remove_spot_from_all_queues(queues, spot)
                        operators_tried = 0
                    else:
                        operators_tried += 1
                elif operators_tried >= operators_count:
                    print('Could not assign all spots to operators due to capacity constraint')
                elif queue.empty():
                    return routes

        return routes

    def remove_spot_from_all_queues(self, operator_queues, assigned_spot):
        for queue in operator_queues.values():
            queue_elements_buffer = []
            while not queue.empty():
                cost_order_spot_tuple = queue.get()
                if cost_order_spot_tuple[2] != assigned_spot:
                    queue_elements_buffer.append(cost_order_spot_tuple)

            for queue_tuple in queue_elements_buffer:
                queue.put(queue_tuple)

    def prepare_routes_for_map(self, routes, costs):
        # operators = Operator.objects.all()
        # operator_id_to_name = {operator.id: (f"{operator.user.first_name} {operator.user.last_name},"
        #                                      f" km: {float(costs[operator.id] / 1000)}") for operator in operators}
        new_dict = {}
        for operator_id, route in routes.items():
            spots_on_route = []
            for stop in route:
                if isinstance(stop, Operator):
                    spots_on_route.append(
                        {'name': stop.user.first_name + stop.user.last_name + 'km: ' + str(float(costs[stop.id] / 1000)),
                         'address': stop.geo.address, 'lon': stop.geo.geolocation.lon, 'lat': stop.geo.geolocation.lat})
                elif isinstance(stop, Hub):
                    spots_on_route.append({'name': stop.shortcode, 'address': stop.geo.address,
                                           'lon': stop.geo.geolocation.lon, 'lat': stop.geo.geolocation.lat})
                elif isinstance(stop, Spot):
                    spots_on_route.append({'name': stop.shortcode, 'address': stop.location.geo.address,
                                           'lon': stop.location.geo.geolocation.lon,
                                           'lat': stop.location.geo.geolocation.lat})
                else:
                    print('Not a operator, hub or spot')
            operator = Operator.objects.get(id=operator_id)
            key = operator.user.first_name + ' ' +  operator.user.last_name + ' km: ' + str(float(costs[operator_id] / 1000))
            new_dict[key] = spots_on_route
        return new_dict
