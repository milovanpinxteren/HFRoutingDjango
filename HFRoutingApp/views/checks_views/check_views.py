from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.routingclasses.helpers.distance_calculators.distance_matrix_checker import DistanceMatrixChecker


@login_required
def check_distance_matrix(request):
    distance_matrix_checker = DistanceMatrixChecker()
    response = distance_matrix_checker.check_distances()
    print(response)
    return render(request, 'components/checks_response.html', {'response': response})