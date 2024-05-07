class RouteCalculator:
    def compute_routes(self):
        """
        Objectives
        - Minimize Total Travel Costs
        - Maximize Delivery Reliability
        - Minimize Emissions or Environmental Impact
        - Maximize driver familiarity

        Objective: calculate best routes regarding objectives
                    - Given
                        - distance matrix
                        - all stops of a day
                        - penalties per stop (see penalty_calculator.py)
                        - Opening times of customer location
                        - Load per stop (Richard)
                        - Mandatory Driver-stop Assignment (e.g. only 1 driver is allowed to fill a certain stop)

        Constraints:
                    - Vehicle load
                    - max driving time (starting time of driver until 12:30)

        Initial solution Method:
            - Start with mandatory driver-stop assignment
            - Calculate insertion costs (based on extra kilometers + penalty)
            - add stop with lowest insertion cost (until constraints met)
            - When constraint met, move to next driver and compute route (which algorithm?)
            - This is the starting solution
            - How to improve the start solution
                            - Local Search
                            - Simulated Annealing
                            - ABC (Artificial Bee Colony),
                            - ACO (Ant Colony Optimization),
                            - CW (Clarke and Wright Heuristic),
                            - GA (Genetic Algorithm)
                            - PSO (Particle Swarm Optimization)
                            - VNS (Variable Neighborhood Search).

        Cluster method:
        - Make base routes/clusters
        - Based on:
            - number of drivers (this differs per day)
            - number of stops (with removal probability)
            - max number of stops by total travel + fill time
        - For each cluster
            - See which stops are below the threshold
            - Remove stops


        Pro's and Con's
        - Cluster method is less computing time
        - Cluster method is less robust
            - Locations have different filling days (some 2 days, some 3 days)
            - Drivers have different availability (e.g. on monday we have 10 drivers, wednesday 7)
            - Drivers are variable (vacation, sickness, etc)
            - What if a driver has 2 mandatory locations, in different clusters


        """
