from django.db import models
from django.utils.translation import gettext_lazy as _
from django_google_maps import fields as map_fields
from django.contrib.auth.models import User


class Weekday(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Maandag'),
        (1, 'Dinsdag'),
        (2, 'Woensdag'),
        (3, 'Donderdag'),
        (4, 'Vrijdag'),
        (5, 'Zaterdag'),
        (6, 'Zondag'),
    ]
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'{self.get_day_display()}'


class Geo(models.Model):
    geo_id = models.AutoField(primary_key=True)
    address = map_fields.AddressField(_('address'), max_length=200, blank=True, null=True)
    geolocation = map_fields.GeoLocationField(_('geolocation'), max_length=100, blank=True, null=True)

    def __str__(self):
        location = Location.objects.filter(geo=self).first()
        return location.shortcode if location else super().__str__()

class Customer(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.shortcode


class Location(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    geo = models.ForeignKey(Geo, models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True)
    customer = models.ForeignKey(Customer, models.CASCADE, default=None, limit_choices_to={'active': True},
                                 verbose_name=Customer._meta.verbose_name)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    opening_time = models.TimeField(_('opening time'), blank=True, null=True)

    def __str__(self):
        return self.shortcode



class Hub(models.Model):
    geo = models.ForeignKey(Geo, on_delete=models.CASCADE, default=0)
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.shortcode

class Operator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    geo = models.ForeignKey(Geo, on_delete=models.CASCADE, default=0)
    max_vehicle_load = models.IntegerField()
    starting_time = models.TimeField()
    active = models.BooleanField(default=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.user.username


class OperatorGeoLink(models.Model):  # welke chauffeur mag welke route
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    geo = models.ForeignKey(Geo, on_delete=models.CASCADE)



class Spot(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    location = models.ForeignKey(Location, models.CASCADE, default=None, limit_choices_to={'active': True},)
    updated_at = models.DateTimeField(auto_now=True)
    is_catering = models.BooleanField(default=False)
    pilot = models.BooleanField(default=False)
    spot_hours = models.IntegerField(default=0) #if office or hospital
    #Added columns
    fill_dates = models.ManyToManyField(Weekday, blank=True)
    avg_no_crates = models.FloatField(blank=True, null=True)
    fill_time_minutes = models.IntegerField(default=0, blank=True, null=True)
    walking_time_minutes = models.IntegerField(default=0, blank=True, null=True)
    removal_probability = models.FloatField(_('removal probability'), blank=True,
                                            null=True)  # 0-1 used for cluster making and manual override
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.shortcode


class CateringOrder(models.Model):
    delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, default=0)


class CateringOrderLine(models.Model):
    catering_order = models.ForeignKey(CateringOrder, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

class PickListLine(models.Model):
    distr_date = models.DateField()
    quantity = models.IntegerField(default=0)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)

class Route(models.Model):
    name = models.CharField(max_length=100)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    geos = models.ManyToManyField(Geo)
    order = models.CharField(max_length=1000) #array with the stops in driving order
    day = models.DateField()
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, default=0)
    is_base_route = models.BooleanField(default=False)

class DistanceMatrix(models.Model):
    origin = models.ForeignKey(Geo, related_name='distances_from', on_delete=models.CASCADE, default=0)
    destination = models.ForeignKey(Geo, related_name='distances_to', on_delete=models.CASCADE, default=0)
    distance_meters = models.FloatField(null=True)



class OperatorPlanning(models.Model):
    day = models.DateField()
    operators = models.ManyToManyField(Operator, blank=True)

