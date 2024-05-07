from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.map_maker import MapMaker
from HFRoutingApp.models import Hub, Location, Operator


@login_required
def show_map(request):
    map_maker = MapMaker()
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
    map_dict = {'hubs': hub_locations,
                'customers': customer_locations,
                'operators': operator_locations}
    map = map_maker.make_map(map_dict)
    context = {'map': map._repr_html_()}
    return render(request, 'map/map.html', context)
