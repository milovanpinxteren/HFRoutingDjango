from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from HFRoutingApp.classes.map_maker import MapMaker
from HFRoutingApp.models import Hub, Operator, Location


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
        if hub.geo.geolocation:
            hub_locations.append(
                {'name': hub.shortcode, 'address': hub.geo.address, 'lat': hub.geo.geolocation.lat,
                 'lon': hub.geo.geolocation.lon})
    for location in locations:
        if location.geo.geolocation:
            customer_locations.append(
                {'name': location.shortcode, 'address': location.geo.address, 'lat': location.geo.geolocation.lat,
                 'lon': location.geo.geolocation.lon})
    for operator in operators:
        if operator.location.geolocation:
            operator_locations.append(
                {'name': operator.user.username, 'address': operator.geo.address, 'lat': operator.geo.geolocation.lat,
                 'lon': operator.geo.geolocation.lon})
    map_dict = {'hubs': hub_locations,
                'customers': customer_locations,
                'operators': operator_locations}
    map = map_maker.make_map(map_dict, 'full_map')
    context = {'map': map._repr_html_()}
    return render(request, 'map/map.html', context)
