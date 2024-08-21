import os
import django
import googlemaps
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HFRoutingDjango.settings')
django.setup()



import random
from shapely.geometry import Point, Polygon
from HFRoutingApp.models import Geo


class TestDatabaseExtender:
    def __init__(self):
        self.make_geos()
        self.geos = Geo.objects.all()

    def is_near_road(self,lat, lon):
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        gmaps = googlemaps.Client(key=google_api_key, client_secret=google_client_secret)
        # Use the Geocoding API to get place details for the coordinates
        reverse_geocode_result = gmaps.reverse_geocode((lat, lon))

        # Check if the result includes road or address information
        for result in reverse_geocode_result:
            if 'address_components' in result:
                for component in result['address_components']:
                    if 'route' in component['types'] or 'street_address' in component['types']:
                        return True
        return False
    def make_geos(self):
        # Refined bounding box for the Netherlands
        min_lat, max_lat = 51.00, 53.50
        min_lon, max_lon = 3.50, 7.10

        # Define a simple rectangular polygon for the Netherlands
        netherlands_polygon = Polygon([
            (min_lon, min_lat), (max_lon, min_lat),
            (max_lon, max_lat), (min_lon, max_lat)
        ])

        def generate_random_coordinates(n, polygon):
            coordinates = []
            while len(coordinates) < n:
                lat = random.uniform(min_lat, max_lat)
                lon = random.uniform(min_lon, max_lon)
                point = Point(lon, lat)
                if polygon.contains(point):
                    coordinates.append((lat, lon))
            return coordinates

        # Generate 100 random coordinates in the Netherlands
        coordinates = generate_random_coordinates(200, netherlands_polygon)

        # Output the coordinates
        address_counter = 232
        for coord in coordinates:
            address_counter += 1
            lat, lon = coord
            geolocation = f"{lat},{lon}"
            address_line = "address_" + str(address_counter)
            valid = self.is_near_road(lat, lon)
            if valid:
                Geo.objects.create(
                    pk=address_counter,
                    address=address_line,  # Set default value or provide actual address if needed
                    geolocation=geolocation
                )
            else:
                print('not a location', geolocation, address_line)


TestDatabaseExtender()