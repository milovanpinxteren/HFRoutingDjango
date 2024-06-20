
"""
Takes 50 locations in Distance matrix, calculates distance with google maps, checks with original and reports
"""
from HFRoutingApp.models import DistanceMatrix
import random
import googlemaps
from dotenv import load_dotenv
import os
class DistanceMatrixChecker:
    def check_distances(self):
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        gmaps = googlemaps.Client(key=google_api_key, client_secret=google_client_secret)

        response_dict = {}
        incorrect_distances_counter = 0
        random_distance_pairs = self.get_random_distance_matrices()
        for obj in random_distance_pairs:
            origin = (obj.origin.geolocation.lat, obj.origin.geolocation.lon)
            dest = (obj.destination.geolocation.lat, obj.destination.geolocation.lon)
            original_distance = obj.distance_meters
            gmaps_response = gmaps.distance_matrix(origin, dest, mode="driving")
            try:
                distance = gmaps_response['rows'][0]['elements'][0]['distance']['value']
                if abs(original_distance - distance) > 1000: #If the difference is more than 1 kilometer
                    incorrect_distances_counter += 1
                    locations = str(obj.origin_id) + ' - ' + str(obj.destination_id)
                    response_dict[incorrect_distances_counter] = {locations: original_distance - distance}
                    obj.distance_meters = distance
                    obj.save()
            except Exception as e:
                print('CHECK DISTANCES ERROR: ', e)
        if len(response_dict) == 0:
            response_dict[1] = {str(0) + ' - ' + str(0): '50 random plekken gecheckt, 0 incorrecte gevonden'}
        return response_dict

    def get_random_distance_matrices(self):
        count = DistanceMatrix.objects.count()
        random_indices = random.sample(range(count), 50)
        matrices = [DistanceMatrix.objects.all()[i] for i in random_indices]
        return matrices