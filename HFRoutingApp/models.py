from django.db import models
from django.utils.translation import gettext_lazy as _
from django_google_maps import fields as map_fields
from django.contrib.auth.models import User


class Weekday(models.Model):
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (0, 'Sunday'),
    ]

    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'{self.get_day_display()}'


class Hub(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = map_fields.AddressField(_('address'), max_length=200, blank=True, null=True)
    geolocation = map_fields.GeoLocationField(_('geolocation'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.shortcode

class Customer(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    customer_id = models.IntegerField(default=None, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.shortcode


class Location(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    location_id = models.IntegerField(default=None, blank=True, null=True)
    customer = models.ForeignKey(Customer, models.PROTECT, default=None, limit_choices_to={'active': True},
                                 verbose_name=Customer._meta.verbose_name)
    updated_at = models.DateTimeField(auto_now=True)
    address = map_fields.AddressField(_('address'), max_length=200, blank=True, null=True)
    geolocation = map_fields.GeoLocationField(_('geolocation'), max_length=100, blank=True, null=True)
    fill_dates = models.ManyToManyField(Weekday, blank=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    removal_probability = models.FloatField(_('removal probability'), blank=True,
                                            null=True)  # 0-1 used for cluster making and manual override

    def __str__(self):
        return self.shortcode


class Machine(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    machine_id = models.IntegerField(default=None, blank=True, null=True)
    brand = models.CharField(max_length=80)
    manufacturer_serialnumber = models.CharField(max_length=80)
    hostname = models.CharField(max_length=80, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    external_id = models.SmallIntegerField()
    honesty_model = models.BooleanField(default=False)

    def __str__(self):
        return self.shortcode

class LocationGroup(models.Model):
    name = models.CharField(max_length=100)
    locations = models.ManyToManyField(Location)

    def __str__(self):
        return self.name


class Operator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(_('address'), max_length=200, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    geolocation = map_fields.GeoLocationField(_('geolocation'), max_length=100, blank=True, null=True)
    max_vehicle_load = models.IntegerField()
    starting_time = models.TimeField()
    active = models.BooleanField(default=True)
    availability = models.ManyToManyField(Weekday, blank=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return self.user.username


class OperatorLocationLink(models.Model):  # welke chauffeur mag welke route
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)


class Spot(models.Model):
    shortcode = models.CharField(max_length=7)
    description = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    location = models.ForeignKey(Location, models.PROTECT, default=None, limit_choices_to={'active': True},)
    machine = models.ForeignKey(Machine, models.PROTECT, default=None, limit_choices_to={'active': True},)
    updated_at = models.DateTimeField(auto_now=True)
    is_catering = models.BooleanField(default=False)
    activation_date = models.DateField()
    pricelist_id = models.IntegerField(default=None, blank=True, null=True)
    resembles_id = models.IntegerField(default=None, blank=True, null=True)
    product_filter = models.IntegerField(default=None, blank=True, null=True)
    pilot = models.BooleanField(default=False)
    spot_hours = models.IntegerField(default=0)

    def __str__(self):
        return self.shortcode


class CateringOrder(models.Model):
    delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, default=0)


class Route(models.Model):
    name = models.CharField(max_length=100)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location)
    order = models.CharField(max_length=1000) #array with the stops in driving order
    day = models.DateField()