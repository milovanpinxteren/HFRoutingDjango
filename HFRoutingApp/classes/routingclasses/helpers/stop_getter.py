from datetime import datetime
from itertools import chain
from HFRoutingApp.models import Spot, CateringOrderLine, PickListLine

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
                                                                        'catering_order__spot__geo').filter(
            catering_order__delivery_date=date)
        picklist_lines = PickListLine.objects.select_related('spot', 'spot__geo').filter(distr_date=date)
        if not picklist_lines: #If the picklist is unkown -> Return all stops of all locations on date
            picklist_lines = self.get_stops_to_fill(date)

        for obj in chain(catering_order_lines, picklist_lines):
            if obj.__class__.__name__ == 'CateringOrderLine':
                prefix = obj.catering_order.spot
                quantity = obj.quantity
            elif obj.__class__.__name__ == 'PickListLine':
                prefix = obj.spot
                quantity = obj.quantity
            elif obj.__class__.__name__ == 'Spot':
                prefix = obj
                quantity = obj.avg_no_crates
            stop_info = {
                'quantity': quantity,
                'pilot': prefix.pilot,
                'fill_time': prefix.fill_time_minutes,
                'walking_time': prefix.walking_time_minutes,
                'removal_probability': prefix.removal_probability,
                'notes': prefix.notes,
                'location': {
                    'locationID': prefix.geo.id,
                    'shortcode': prefix.geo.shortcode,
                    'description': prefix.geo.description,
                    'notes': prefix.geo.notes,
                    'opening_time': prefix.geo.opening_time,
                    'address': prefix.geo.address,
                    'geolocation': prefix.geo.geolocation,
                }
            }
            stops[prefix.id] = stop_info
        return {
            'date': date,
            'stops': stops,
        }

    def get_stops_to_fill(self, date):
        weekday = datetime.strptime(date, '%Y-%m-%d').weekday() #(0 = Monday, 6 = Sunday)
        spots = Spot.objects.filter(fill_dates=weekday)

        return spots
