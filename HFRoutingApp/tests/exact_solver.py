import os
import django
import itertools

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HFRoutingDjango.settings')
django.setup()

from HFRoutingApp.classes.routingclasses.helpers.calculate_cost_per_route import CalculateCostPerRoute
from HFRoutingApp.views.routing_views.calculate_routes_views import generate_start_route_for_tuner


class ExactSolver:
    def __init__(self, date):
        self.routes = self._initialize_routes(date)
        print('ROUTES: ', self.routes)

    def _initialize_routes(self, date):
        # Generate initial routes for the given date
        return generate_start_route_for_tuner(date)

    def solve(self):
        drivers = list(self.routes.keys())  # List of driver IDs
        routes = list(self.routes.values())  # List of stops for each driver

        # Prepare to store the fixed parts of each route and the permutable parts
        fixed_parts = []
        middle_parts = []

        # Extract the fixed and permutable parts for each driver
        for route in routes:
            if len(route) > 4:  # Ensure the route has enough stops
                fixed_start = route[:2]  # First two stops (driver location)
                fixed_end = route[-2:]    # Last two stops (hub location)
                middle = route[2:-2]      # Middle stops to permute

                fixed_parts.append((fixed_start, fixed_end))
                middle_parts.append(middle)
            else:
                raise ValueError("Each route must have at least 5 stops (2 fixed at the start, 2 fixed at the end).")

        # Generate all possible permutations of the middle parts (the stops to permute)
        all_middle_permutations = list(itertools.permutations(middle_parts))
        print(f"Number of middle permutations: {len(all_middle_permutations)}")

        # Initialize the cost calculator
        cost_calculator = CalculateCostPerRoute()

        best_permutation = None
        best_cost = float("inf")
        perm_counter = 0
        perm_dict = {}

        # Evaluate each permutation
        for perm in all_middle_permutations:
            perm_counter += 1
            permuted_routes = {}

            # Reconstruct the full routes with fixed start/end and permuted middle
            for i, driver in enumerate(drivers):
                fixed_start, fixed_end = fixed_parts[i]
                middle_permutation = perm[i]
                full_route = fixed_start + list(middle_permutation) + fixed_end
                permuted_routes[driver] = full_route

            # Calculate the cost of the current permutation
            cost = cost_calculator.calculate_cost_per_route(permuted_routes)['total']
            perm_dict[perm_counter] = cost
            if perm_counter % 1000 == 0:
                print(f"Permutation {perm_counter}, perm_dict {perm_dict}")

            # Update best solution if the current one is better
            if cost < best_cost:
                best_cost = cost
                best_permutation = permuted_routes
                print(f"Permutation {perm_counter}, Cost: {cost}: {permuted_routes}")

        return best_permutation, best_cost


# Example usage
solver = ExactSolver('2024-06-19')
best_routes, best_cost = solver.solve()

print(f"Best Route Assignment: {best_routes}")
print(f"Best Cost: {best_cost}")
