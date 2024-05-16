from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from HFRoutingApp.classes.routingclasses.distance_calculators.distance_matrix_checker import DistanceMatrixChecker


@login_required
def check_distance_matrix(request):
    distance_matrix_checker = DistanceMatrixChecker()
    distance_matrix_checker.check_distances()
    return HttpResponse('Check')