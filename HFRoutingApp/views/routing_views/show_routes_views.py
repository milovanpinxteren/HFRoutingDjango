from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from HFRoutingApp.classes.map_maker import MapMaker
from HFRoutingApp.models import Route


@login_required
def show_routes_page(request):
    return render(request, 'routes/routes.html')


@login_required
def show_routes_for_date(request):
    map_maker = MapMaker()
    date = request.GET.get('date', None)
    response_data = {}
    map_data = {}
    routes = Route.objects.filter(day=date)
    for route in routes:
        locations_dict = {}
        map_data[route.name] = []
        geos = route.geos.values()
        for geo in geos:
            info_dict = {'name': geo['shortcode'], 'address': geo['address'],
                                              'lat': geo['geolocation'].lat,
                                              'lon': geo['geolocation'].lon}
            locations_dict[geo['id']] = info_dict
            map_data[route.name].append(info_dict)
        response_data[route.id] = {'id': route.id, 'hub': route.hub,'name': route.name, 'order': route.order, 'day': route.day,
                                   'operator': route.operator.user.username, 'locations': locations_dict}
    map_obj = map_maker.make_map(map_data, 'routes')
    response = {'day': date, 'routes': response_data, 'map': map_obj._repr_html_()}
    return render(request, 'routes/routes_overview.html', response)
