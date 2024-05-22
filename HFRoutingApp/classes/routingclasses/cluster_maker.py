from HFRoutingApp.models import Location, Hub
from sklearn.cluster import KMeans
import numpy as np


class ClusterMaker:
    def make_clusters(self, no_clusters):
        locations = Location.objects.filter(active=True)
        self.hubs = Hub.objects.filter(location__active=True).select_related('location')

        customer_locations = []
        for location in locations:
            if location.geolocation:
                customer_locations.append(
                    {'name': location.shortcode, 'address': location.address, 'lat': location.geolocation.lat,
                     'lon': location.geolocation.lon})

        coords = [(loc['lat'], loc['lon']) for loc in customer_locations]
        kmeans = KMeans(n_clusters=no_clusters, random_state=42)
        kmeans.fit(coords)
        labels = kmeans.labels_

        clusters = {}
        for label, loc in zip(labels, customer_locations):
            cluster_label = f'Cluster{label + 1}'
            if cluster_label not in clusters:
                clusters[cluster_label] = []
            clusters[cluster_label].append({
                'name': loc['name'],
                'address': loc['address'],
                'lat': loc['lat'],
                'lon': loc['lon']
            })

        for cluster_label in clusters:
            closest_hub = self.select_hub_for_cluster(clusters[cluster_label])
            clusters[cluster_label].append(closest_hub)
            clusters[cluster_label] = self.sort_locations_by_proximity_to_hub(closest_hub, clusters[cluster_label])
        return clusters

    def select_hub_for_cluster(self, cluster):
        # Select the hub closest to the center of the cluster
        cluster_points = [(loc['lat'], loc['lon']) for loc in cluster]
        cluster_center = [np.mean([point[i] for point in cluster_points]) for i in range(2)]
        closest_hub, min_distance = None, float('inf')
        for hub in self.hubs:
            distance = np.linalg.norm(
                np.array(cluster_center) - np.array([hub.location.geolocation.lat, hub.location.geolocation.lon]))
            if distance < min_distance:
                closest_hub = hub
                min_distance = distance
        hub_info = {
            'name': closest_hub.shortcode,
            'address': closest_hub.location.address,
            'lat': closest_hub.location.geolocation.lat,
            'lon': closest_hub.location.geolocation.lon
        }
        return hub_info

    def sort_locations_by_proximity_to_hub(self, hub, locations):
        # Compute the distance from each location to the hub
        location_distances = []
        for location in locations:
            distance = np.linalg.norm(np.array([hub['lat'], hub['lon']]) - np.array([location['lat'], location['lon']]))
            location_distances.append((location, distance))

        locations_sorted_by_distance = [loc for loc, dist in sorted(location_distances, key=lambda x: x[1])]

        return locations_sorted_by_distance
