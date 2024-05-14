from django.urls import path
from .views.main_views import *
from HFRoutingApp.views.map_views.show_map_views import *
from HFRoutingApp.views.routing_views.show_routes_views import *
from HFRoutingApp.views.routing_views.calculate_routes_views import *

urlpatterns = [
    path("", index, name="index"),
    path("show_map", show_map, name="show_map"),

    path("show_routes_page", show_routes_page, name="show_routes_page"),
    path("show_routes_for_date", show_routes_for_date, name="show_routes_for_date"),
    path("calculate_routes_for_date", calculate_routes_for_date, name="calculate_routes_for_date"),
    path("make_clusters", calculate_clusters, name="make_clusters"),
    path("make_base_routes", make_base_routes, name="make_base_routes"),

]
