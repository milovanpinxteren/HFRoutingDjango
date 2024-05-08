import datetime

from django.test import TestCase, Client
from django.contrib.auth.models import User

from HFRoutingApp.models import Location, Machine, Spot


class CalculateRoutesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.location = Location.objects.create(
            shortcode='L1',
            description='Location 1',
            active=True,
            customer_id=1,  # Assuming that a Customer with id=1 exists
            address='123 Fake Street, Faketown',
            geolocation='POINT (30 10)',  # Dummy geolocation
            notes='Test notes',
            opening_time=datetime.time(9, 0),  # 9:00 AM
            removal_probability=0.5
        )
        self.machine = Machine.objects.create(shortcode='M1', description='Machine 1', active=True)
        self.spot = Spot.objects.create(shortcode='S1', description='Spot 1', location=self.location,
                                        machine=self.machine, is_catering=False)

    def test_generate_route(self):
        self.client.login(username='testuser', password='12345')
        date = '2024-05-12'
        response = self.client.get('/calculate_routes_for_date', {'date': date})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stops'], 6)

        # DAYS_OF_WEEK = [
        #     (0, 'Maandag'),
        #     (1, 'Dinsdag'),
        #     (2, 'Woensdag'),
        #     (3, 'Donderdag'),
        #     (4, 'Vrijdag'),
        #     (5, 'Zaterdag'),
        #     (6, 'Zondag'),
        # ]
