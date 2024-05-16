from itertools import islice
from django.db.models import Value

import googlemaps
from dotenv import load_dotenv
import os
from HFRoutingApp.models import Location, Hub, DistanceMatrix


class DistanceMatrixUpdater:
    def chunks(self, data, size=25):
        dict_items = list(data.items())
        return [dict(dict_items[i:i + size]) for i in range(0, len(dict_items), size)]

    def update_distances(self):
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

        locations = Location.objects.filter(active=True).annotate(model=Value('Location')).values_list(
            'customer__shortcode', 'id',
            'shortcode', 'geolocation')

        gmaps = googlemaps.Client(key=google_api_key, client_secret=google_client_secret)
        geolocations = {}
        for location in list(locations):
            geolocations[location[1]] = {'customer__shortcode': location[0], 'shortcode': location[2],
                                         'lat': location[3].lat, 'lon': location[3].lon}

        geolocation_chunks = self.chunks(geolocations)
        all_distances_dict = {}
        for origin_location_id, origin_info in geolocations.items():
            location_distance_dict = {}
            for chunk in geolocation_chunks:
                destinations = [(destination_info['lat'], destination_info['lon'])
                                for destination_id, destination_info in chunk.items()]
                gmaps_response = gmaps.distance_matrix((origin_info['lat'], origin_info['lon']), destinations,
                                                       mode="driving")
                for index, distance_row in enumerate(gmaps_response['rows'][0]['elements']):
                    distance = distance_row['distance']['value']
                    destination_id = list(chunk.keys())[index]
                    location_distance_dict[destination_id] = distance
            all_distances_dict[origin_location_id] = location_distance_dict
        self.save_distances(all_distances_dict)



    def save_distances(self, all_distances_dict):
        for origin_id, destinations in all_distances_dict.items():
            origin = Location.objects.get(id=origin_id)
            for destination_id, distance in destinations.items():
                destination = Location.objects.get(id=destination_id)
                DistanceMatrix.objects.update_or_create(origin=origin, destination=destination,
                                                        defaults={'distance_meters': distance})
        return 'Distances saved'