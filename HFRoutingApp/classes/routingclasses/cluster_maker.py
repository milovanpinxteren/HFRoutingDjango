from HFRoutingApp.models import Location, Hub
from sklearn.cluster import KMeans
from collections import defaultdict
import random
import numpy as np
from scipy.spatial import distance_matrix


class ClusterMaker:
    def make_clusters(self, no_clusters):
        locations = Location.objects.filter(active=True)
        self.hubs = Hub.objects.filter(active=True)

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
        return clusters

    def select_hub_for_cluster(self, cluster):
        # Select the hub closest to the center of the cluster
        cluster_points = [(loc['lat'], loc['lon']) for loc in cluster]
        cluster_center = [np.mean([point[i] for point in cluster_points]) for i in range(2)]
        closest_hub, min_distance = None, float('inf')
        for hub in self.hubs:
            distance = np.linalg.norm(np.array(cluster_center) - np.array([hub.geolocation.lat, hub.geolocation.lon]))
            if distance < min_distance:
                closest_hub = hub
                min_distance = distance
        hub_info = {
                'name': closest_hub.shortcode,
                'address': closest_hub.address,
                'lat': closest_hub.geolocation.lat,
                'lon': closest_hub.geolocation.lon
        }
        return hub_info


