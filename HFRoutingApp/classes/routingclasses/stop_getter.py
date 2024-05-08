from django.db.models import Q
from datetime import datetime

from HFRoutingApp.models import Machine, Spot, Location


class StopGetter:
    def get_stops_on_date(self, date):
        # TODO: check if date is in picklist or cateringorders
        #TODO: start time of driver -> not yet incorporated but needs to

        return