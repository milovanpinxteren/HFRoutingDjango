from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.routingclasses.penalty_calculator import PenaltyCalculator
from HFRoutingApp.classes.routingclasses.stop_getter import StopGetter



@login_required
def calculate_routes_for_date(request):
    stop_getter = StopGetter()
    # penalty_calculator = PenaltyCalculator()
    date = request.GET.get('date', None)
    stops = stop_getter.get_stops_on_date(date)
    # TODO: assign stop to hub in crate is underway to hub

    context = {'stops': stops}
    return render(request, 'routes/routes_overview.html', context)