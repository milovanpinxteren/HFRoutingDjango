from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.routingclasses.penalty_calculator import PenaltyCalculator
from HFRoutingApp.classes.routingclasses.stop_getter import StopGetter



@login_required
def calculate_routes_for_date(request):
    stop_getter = StopGetter()
    penalty_calculator = PenaltyCalculator()
    date = request.GET.get('date', None)
    print(date)
    #TODO: get all stops
    #TODO: calculate penalty for each stop
    return render(request, 'routes/routes_overview.html')