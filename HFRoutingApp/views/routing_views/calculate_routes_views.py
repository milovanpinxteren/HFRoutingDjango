from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.decisionmaker_classes.decision_maker import DecisionMaker
from HFRoutingApp.classes.map_maker import MapMaker
from HFRoutingApp.classes.routingclasses.base_route_maker.mandatory_route_maker import MandatoryRouteMaker
from HFRoutingApp.classes.routingclasses.base_route_maker.route_extender import RouteExtender
from HFRoutingApp.classes.routingclasses.cluster_maker import ClusterMaker
from HFRoutingApp.classes.routingclasses.helpers.operator_quantity_checker import OperatorQuantityChecker
from HFRoutingApp.classes.routingclasses.helpers.stop_getter import StopGetter



def generate_start_route_for_tuner(date):
    print('Gen for tuner')
    stop_getter = StopGetter()
    stops = stop_getter.get_stops_on_date(date)

    mandatory_route_maker = MandatoryRouteMaker()
    route_extender = RouteExtender()
    print('making mandatory routes', stops)
    routes, remaining_spots, operators = mandatory_route_maker.make_mandatory_routes(stops, date)
    extended_routes = route_extender.extend_route(routes, remaining_spots, operators)
    return extended_routes


@login_required
def calculate_routes_for_date(request):
    # try:
    print('calculate for dates')
    stop_getter = StopGetter()

    date = request.GET.get('date', None)
    stops = stop_getter.get_stops_on_date(date)
    operator_quantity_checker = OperatorQuantityChecker()
    capacity_exceeded, message = operator_quantity_checker.check(date)

    if capacity_exceeded:
        context = {'routes': False, 'message': message}
        return render(request, 'routes/routes_overview.html', context)
    elif not capacity_exceeded and message:
        context = {'message': message}

    mandatory_route_maker = MandatoryRouteMaker()
    route_extender = RouteExtender()
    map_maker = MapMaker()
    print('making mandatory routes', stops)
    routes, remaining_spots, operators = mandatory_route_maker.make_mandatory_routes(stops, date)
    extended_routes, route_with_spots = route_extender.extend_route(routes, remaining_spots, operators)

    routes_map = map_maker.make_map(extended_routes, 'routes')

    context.update({'routes': True, 'map': routes_map._repr_html_()})
    # except Exception as e:
    #     print(e)
    #     context = {'routes': False, 'message': e}
    return render(request, 'routes/routes_overview.html', context)


@login_required
def calculate_clusters(request):
    cluster_maker = ClusterMaker()
    map_maker = MapMaker()
    no_clusters = int(request.GET.get('no_clusters', 6))
    clusters = cluster_maker.make_clusters(no_clusters)
    clusters_map = map_maker.make_map(clusters, 'routes')
    response = {'routes': True,'map': clusters_map._repr_html_()}
    return render(request, 'routes/routes_overview.html', response)

@login_required
def make_base_routes(request):
    print('Make base routes triggered')
    mandatory_route_maker = MandatoryRouteMaker()
    route_extender = RouteExtender()
    map_maker = MapMaker()

    routes, remaining_spots, operators = mandatory_route_maker.make_mandatory_routes(False, False)
    extended_routes = route_extender.extend_route(routes, remaining_spots, operators)
    routes_map = map_maker.make_map(extended_routes, 'routes')

    context = {'routes': True, 'map': routes_map._repr_html_()}
    return render(request, 'routes/routes_overview.html', context)