from django.urls import path
from .views.main_views import *
from .views.show_map_views import *
from .views.show_routes_views import *

urlpatterns = [
    path("", index, name="index"),
    path("show_map", show_map, name="show_map"),
    path("show_routes_page", show_routes_page, name="show_routes_page"),
]
