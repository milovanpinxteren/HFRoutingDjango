from django.db.models import Q
from datetime import datetime
from itertools import chain
from HFRoutingApp.models import Machine, Spot, Location, CateringOrder, CateringOrderLine, PickListLine

'''
Gets all the stops for a date based on occurrence in Cateringorders and Picklist.
returns a dict with all the stops for a date.
{'date': '2024-05-14',
'stops': {
        spotID: {
                'quantity': quantity,
                'pilot': True/False,
                'fill_time': fill_time,
                'walking_time': walking_time,
                'removal_probability': removal_probability,
                'notes': notes,
                'location': {
                            'locationID': locationID,
                            'shortcode': shortcode,
                            'description': description,
                            'notes': notes,
                            'opening_time': opening_time,
                            'address': address
                            'geolocation': geolocation,
                            }
                }
        }
}
'''


class StopGetter:
    def get_stops_on_date(self, date):
        stops = {}
        catering_order_lines = CateringOrderLine.objects.select_related('catering_order__spot',
                                                                        'catering_order__spot__location').filter(
            catering_order__delivery_date=date)
        picklist_lines = PickListLine.objects.select_related('spot', 'spot__location').filter(distr_date=date)

        for obj in chain(catering_order_lines, picklist_lines):
            if obj.__class__.__name__ == 'CateringOrderLine':
                prefix = obj.catering_order
            elif obj.__class__.__name__ == 'PickListLine':
                prefix = obj
            stop_info = {
                'quantity': obj.quantity,
                'pilot': prefix.spot.pilot,
                'fill_time': prefix.spot.fill_time_minutes,
                'walking_time': prefix.spot.walking_time_minutes,
                'removal_probability': prefix.spot.removal_probability,
                'notes': prefix.spot.notes,
                'location': {
                    'locationID': prefix.spot.location.id,
                    'shortcode': prefix.spot.location.shortcode,
                    'description': prefix.spot.location.description,
                    'notes': prefix.spot.location.notes,
                    'opening_time': prefix.spot.location.opening_time,
                    'address': prefix.spot.location.address,
                    'geolocation': prefix.spot.location.geolocation,
                }
            }
            stops[prefix.spot.id] = stop_info
        return {
            'date': date,
            'stops': stops,
        }
