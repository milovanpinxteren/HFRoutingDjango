from django.contrib import admin
from .models import Weekday, Customer, Location, Operator, OperatorLocationLink, User, CateringOrder, \
    Hub, Machine, Spot, Route


class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]


class LocationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Location._meta.fields]


class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]


class OperatorLocationLinkAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OperatorLocationLink._meta.fields]

class CateringOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CateringOrder._meta.fields]

class HubAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Hub._meta.fields]

class MachineAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Machine._meta.fields]

class SpotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Spot._meta.fields]

class RouteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Route._meta.fields]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(OperatorLocationLink, OperatorLocationLinkAdmin)
admin.site.register(CateringOrder, CateringOrderAdmin)
admin.site.register(Hub, HubAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Spot, SpotAdmin)
admin.site.register(Route, RouteAdmin)