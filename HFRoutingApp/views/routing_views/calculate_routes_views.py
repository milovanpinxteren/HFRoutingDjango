from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.map_maker import MapMaker
from HFRoutingApp.classes.routingclasses.base_route_maker import BaseRouteMaker
from HFRoutingApp.classes.routingclasses.cluster_maker import ClusterMaker
from HFRoutingApp.classes.routingclasses.penalty_calculator import PenaltyCalculator
from HFRoutingApp.classes.routingclasses.stop_getter import StopGetter



@login_required
def calculate_routes_for_date(request):
    stop_getter = StopGetter()
    # penalty_calculator = PenaltyCalculator()
    date = request.GET.get('date', None)
    stops = stop_getter.get_stops_on_date(date)

    context = {'stops': stops}
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

def make_base_routes(request):
    base_route_maker = BaseRouteMaker()
    base_route_maker.make_base_routes()
    context = {'routes': False}
    return render(request, 'map/map.html', context)