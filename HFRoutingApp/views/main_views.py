from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from HFRoutingApp.models import Hub, Location, Operator


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def show_map(request):
    hubs = Hub.objects.all()
    locations = Location.objects.filter(active=True)
    operators = Operator.objects.filter(active=True)
    hub_locations = []
    customer_locations = []
    operator_locations = []
    for hub in hubs:
        if hub.geolocation:
            hub_locations.append(
                {'name': hub.shortcode, 'address': hub.address, 'lat': hub.geolocation.lat, 'lon': hub.geolocation.lon})
    for location in locations:
        if location.geolocation:
            customer_locations.append(
                {'name': location.shortcode, 'address': location.address, 'lat': location.geolocation.lat,
                 'lon': location.geolocation.lon})
    for operator in operators:
        if operator.geolocation:
            operator_locations.append(
                {'name': operator.user.username, 'address': operator.address, 'lat': operator.geolocation.lat,
                 'lon': operator.geolocation.lon})
    print(hub_locations)
    print(customer_locations)
    print(operator_locations)
    #TODO: pass to class and construct map with folium

    return render(request, 'map/map.html')
