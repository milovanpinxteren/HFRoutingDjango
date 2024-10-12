import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HFRoutingDjango.settings')
django.setup()

import googlemaps
from django.contrib.auth.models import User
from dotenv import load_dotenv

import random
from shapely.geometry import Point, Polygon
from HFRoutingApp.models import Geo, Location, Customer, Spot, Operator, OperatorGeoLink, Hub


class TestDatabaseExtender:
    def __init__(self):
        self.locations_to_generate = 0
        self.operators_to_generate = 2
        self.hubs_to_generate = 2
        self.make_geos()
        self.geos = Geo.objects.all()
        #make operators and operatorgeolink
        self.make_operators()
        #make hubs
        self.make_hubs()
        #fill distance matrix

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
        coordinates = generate_random_coordinates(self.locations_to_generate, netherlands_polygon)

        # Output the coordinates
        address_counter = 232
        for coord in coordinates:
            address_counter += 1
            lat, lon = coord
            geolocation = f"{lat},{lon}"
            address_line = "address_" + str(address_counter)
            valid = self.is_near_road(lat, lon)
            # valid = True
            if valid:
                Geo.objects.create(
                    pk=address_counter,
                    address=address_line,  # Set default value or provide actual address if needed
                    geolocation=geolocation
                )
                Customer.objects.create(pk=address_counter, shortcode=address_counter,
                                        description='test')

                Location.objects.create(pk=address_counter, shortcode=address_counter,
                                        geo=Geo.objects.get(pk=address_counter), description='test',
                                        customer=Customer.objects.get(pk=address_counter))
                Spot.objects.create(pk=address_counter, shortcode=address_counter,
                                    description='test', location=Location.objects.get(pk=address_counter),
                                    avg_no_crates=2, fill_time_minutes=15, walking_time_minutes=15
                                    )
                #
            else:
                print('not a location', geolocation, address_line)

    def make_operators(self):
        for i in range(self.operators_to_generate):
            # Create Geo for operator
            lat = random.uniform(51.00, 53.50)
            lon = random.uniform(3.50, 7.10)
            id = 9900 + i
            valid = self.is_near_road(lat, lon)
            # valid = True
            if valid:
                geo = Geo.objects.create(
                    pk=id,
                    address=f"Operator address {i}",
                    geolocation=f"{lat},{lon}"
                )

                # Create User for operator
                username = f"operator_user_{i}"
                user = User.objects.create_user(
                    pk=id,
                    username=username,
                    password="testpassword123"
                )

                # Create Operator
                operator = Operator.objects.create(
                    pk=id,
                    user=user,
                    geo=geo,
                    max_vehicle_load=random.randint(500, 1000),
                    starting_time="08:00"
                )

                OperatorGeoLink.objects.create(
                    pk=id,
                    operator=operator,
                    geo=geo
                )

    def make_hubs(self):
        for i in range(self.hubs_to_generate):
            id = 9800 + i
            # Create Geo for hub
            lat = random.uniform(51.00, 53.50)
            lon = random.uniform(3.50, 7.10)
            valid = self.is_near_road(lat, lon)
            # valid = True
            if valid:
                geo = Geo.objects.create(
                    pk=id,
                    address=f"Hub address {i}",
                    geolocation=f"{lat},{lon}"
                )

                # Create Hub
                Hub.objects.create(
                    pk=id,
                    geo=geo,
                    shortcode=f"HUB_{i}",
                    description=f"Test Hub {i}"
                )


TestDatabaseExtender()