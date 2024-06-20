from itertools import islice
from django.db.models import Value

import googlemaps
from dotenv import load_dotenv
import os
from HFRoutingApp.models import Geo, DistanceMatrix


class DistanceMatrixUpdater:
    def chunks(self, data, size=25):
        dict_items = list(data.items())
        return [dict(dict_items[i:i + size]) for i in range(0, len(dict_items), size)]

    def update_distances(self):
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        gmaps = googlemaps.Client(key=google_api_key, client_secret=google_client_secret)
        geolocations = {}

        locations = Geo.objects.all().annotate(model=Value('Location')).values_list(
            'geo_id',
            'geolocation')
        for location in list(locations):
            geolocations[location[0]] = {'lat': location[1].lat, 'lon': location[1].lon}

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
                    destination_id = list(chunk.keys())[index]
                    if distance_row['status'] == 'OK':
                        distance = distance_row['distance']['value']
                        location_distance_dict[destination_id] = distance
                    else:
                        location_distance_dict[destination_id] = float('inf')
            all_distances_dict[origin_location_id] = location_distance_dict
        self.save_distances(all_distances_dict)
        return 'Distance Matrix Updated'



    def save_distances(self, all_distances_dict):
        for origin_id, destinations in all_distances_dict.items():
            origin = Geo.objects.get(geo_id=origin_id)
            for destination_id, distance in destinations.items():
                destination = Geo.objects.get(geo_id=destination_id)
                DistanceMatrix.objects.update_or_create(origin=origin, destination=destination,
                                                        defaults={'distance_meters': distance})
        return 'Distances saved'