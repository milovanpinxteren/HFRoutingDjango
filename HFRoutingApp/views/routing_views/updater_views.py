
"""
Views for updating data for routing. E.G. Distance matrix, geolocations, etc
"""
from django.http import HttpResponse

from HFRoutingApp.classes.routingclasses.distance_calculators.distance_matrix_updater import DistanceMatrixUpdater


def update_distance_matrix(request):
    print('UPDATE DISTANCE MATRIX')
    distance_matrix_updater = DistanceMatrixUpdater()
    response = distance_matrix_updater.update_distances()
    return HttpResponse(response)