from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Min

from HFRoutingApp.models import DistanceMatrix, Operator, Hub, Location


class GroupAssigner:
    def assign_groups(self, routes, remaining_spots, operators):
        print(routes)
        remote_geos = DistanceMatrix.objects.filter(Q(distance_meters__gt=0) & Q(distance_meters__lt=500))
        for geo_pair in remote_geos:
            distance_to_operators = DistanceMatrix.objects.filter(origin=geo_pair.origin_id, destination__geo_id__in=list(operators.values_list('id', flat=True)))
            min_distance_pair = distance_to_operators.aggregate(Min('distance_meters'))

            shortest_pair = distance_to_operators.filter(distance_meters=min_distance_pair['distance_meters__min']).first()
            origin_id = shortest_pair.origin_id
            destination_id = shortest_pair.destination_id
            operator = Operator.objects.get(Q(id=destination_id) | Q(id=origin_id))
            try:
                Hub.objects.get(geo_id=origin_id)
            except ObjectDoesNotExist:
                try:
                    Hub.objects.get(geo_id=destination_id)
                except ObjectDoesNotExist:
                    try:
                        Operator.objects.get(geo_id=origin_id)
                    except ObjectDoesNotExist:
                        try:
                            Operator.objects.get(geo_id=destination_id)
                        except ObjectDoesNotExist:
                            origin_exists_in_route = False
                            destination_exists_in_route = False
                            if (any(geo_pair.origin in route for route in routes.values())):
                                origin_exists_in_route = True
                            elif (any(geo_pair.destination in route for route in routes.values())):
                                destination_exists_in_route = True
                            if not origin_exists_in_route and not destination_exists_in_route:
                                origin_location = Location.objects.get(geo_id=origin_id)
                                if origin_location is not None:
                                    routes[operator.id].insert(2, geo_pair.origin)
                                    remaining_spots = remaining_spots.exclude(location__geo=geo_pair.origin)
                                destination_location = Location.objects.get(geo_id=origin_id)
                                if destination_location is not None:
                                    routes[operator.id].insert(2, geo_pair.destination)
                                    remaining_spots = remaining_spots.exclude(location__geo=geo_pair.destination)
                            elif origin_exists_in_route and not destination_exists_in_route:
                                destination_location = Location.objects.get(geo_id=origin_id)
                                if destination_location is not None:
                                    routes[operator.id].insert(2, geo_pair.destination)
                                    remaining_spots = remaining_spots.exclude(location__geo=geo_pair.destination)
                            elif not origin_exists_in_route and destination_exists_in_route:
                                origin_location = Location.objects.get(geo_id=origin_id)
                                if origin_location is not None:
                                    routes[operator.id].insert(2, geo_pair.origin)
                                    remaining_spots = remaining_spots.exclude(location__geo=geo_pair.origin)
                            else:
                                print(f'both origin ({geo_pair.origin_id}) and destination ({geo_pair.destination_id}) already routed')

                # for operator_id, route in routes.items():
                            # if geo_pair.origin in route and not geo_pair.destination in route:
                            #     routes[operator.id].insert(2, geo_pair.destination)
                            # elif geo_pair.destination in route and not geo_pair.origin in route:
                            #     routes[operator.id].insert(2, geo_pair.origin)
                            # elif geo_pair.origin in route and geo_pair.destination in route:
                            #     routed = True
                            #     print(f'both origin ({geo_pair.origin_id}) and destination ({geo_pair.destination_id}) already routed')
                            # elif not geo_pair.origin in route and not geo_pair.destination in route:
                            #     routes[operator.id].insert(2, geo_pair.destination)
                            #     routes[operator.id].insert(2, geo_pair.origin)


                    # if not any(geo_pair.origin in route for route in routes.values()):
                    #     routes[operator.id].insert(2, geo_pair.origin)
                    # if not any(geo_pair.destination in route for route in routes.values()):
                    #     routes[operator.id].insert(2, geo_pair.destination)

        return routes, remaining_spots