from django.test import TestCase

from HFRoutingApp.classes.routingclasses.route_optimizer.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class GeneticAlgorithmTest(TestCase):
    fixtures = ['db_dump.json']

    def test_genetic_algorithm(self):
        routes = {6: [329, 322, 322, 329, 256, 315, 281, 244, 253],
                  4: [331, 324, 276, 324, 331, 313, 310, 274, 317, 289],
                  7: [328, 323, 267, 323, 328, 285, 280, 312, 312, 264],
                  5: [330, 322, 322, 330, 246, 260, 257],
                  1: [290, 322, 322, 290, 246, 300, 311, 301, 244],
                  2: [290, 322, 263, 306, 306, 322, 290, 315, 255, 311, 284],
                  9: [326, 323, 323, 326, 286, 271, 268, 320],
                  8: [327, 325, 287, 287, 298, 325, 327, 302, 302, 305, 241]}

        self.genetic_algorithm = GeneticAlgorithm()
        optimized_routes = self.genetic_algorithm.do_evolution(routes)
