from django.contrib import admin
from .models import Weekday, Customer, Operator, OperatorGeoLink, User, CateringOrder, \
    Hub, Spot, Route, OperatorPlanning, Geo


class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]


class GeoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Geo._meta.fields]


class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]


class OperatorGeoLinkAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OperatorGeoLink._meta.fields]

class CateringOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CateringOrder._meta.fields]

class HubAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Hub._meta.fields]

# class MachineAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Machine._meta.fields]

class SpotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Spot._meta.fields]

class RouteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Route._meta.fields]

class OperatorPlanningAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OperatorPlanning._meta.fields]

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Geo, GeoAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(OperatorGeoLink, OperatorGeoLinkAdmin)
admin.site.register(CateringOrder, CateringOrderAdmin)
admin.site.register(Hub, HubAdmin)
# admin.site.register(Machine, MachineAdmin)
admin.site.register(Spot, SpotAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(OperatorPlanning, OperatorPlanningAdmin)