from django.urls import path
from .views.main_views import *
from HFRoutingApp.views.map_views.show_map_views import *
from HFRoutingApp.views.routing_views.show_routes_views import *

urlpatterns = [
    path("", index, name="index"),
    path("show_map", show_map, name="show_map"),
    path("show_routes_page", show_routes_page, name="show_routes_page"),
    path("show_routes_for_date", show_routes_for_date, name="show_routes_for_date"),

]
