from django.db.models import Sum

from HFRoutingApp.classes.routingclasses.helpers.route_utils import RouteUtils
from HFRoutingApp.models import Operator, CateringOrderLine, PickListLine, CateringOrder, Spot, Hub


class OperatorQuantityChecker:
    def __init__(self):
        self.route_utils = RouteUtils()

    def check(self, date):
        max_capacity = 0
        crates_needed = 0
        if date:
            operators = Operator.objects.filter(active=True, operatorplanning__day=date)
            hub_geos = Hub.objects.values_list('geo', flat=True)
            catering_orders = CateringOrder.objects.filter(delivery_date=date).exclude(spot__location__geo__in=hub_geos)
            grouped_catering_orders = catering_orders.values('spot').annotate(
                sum_quantity=Sum('cateringorderline__quantity'))
            pick_list_lines = PickListLine.objects.filter(distr_date=date)
            grouped_pick_list_lines = pick_list_lines.values('spot').annotate(sum_quantity=Sum('quantity'))

            for operator in operators:
                max_capacity += operator.max_vehicle_load

            for catering_order in grouped_catering_orders:  # max 35
                try:
                    catering_order_crates_needed = 0
                    if catering_order['sum_quantity'] <= 35:
                        catering_order_crates_needed = 1
                    else:
                        catering_order_crates_needed += (catering_order['sum_quantity'] // 35) + 1
                    crates_needed += catering_order_crates_needed
                    spot = Spot.objects.get(id=catering_order['spot'])
                    spot.avg_no_crates = (spot.avg_no_crates + catering_order_crates_needed) * 0.5
                    spot.save()
                except TypeError:
                    crates_needed += 0

            for line in grouped_pick_list_lines:  # max 35
                fridge_crates_needed = 0
                if line['sum_quantity'] <= 35:
                    fridge_crates_needed += 1
                else:
                    fridge_crates_needed += (line['sum_quantity'] // 35) + 1
                crates_needed += fridge_crates_needed
                spot = Spot.objects.get(id=line['spot'])
                spot.avg_no_crates = (spot.avg_no_crates + fridge_crates_needed) * 0.5
                spot.save()
            print('crates needed: ', crates_needed)
            print('driver cap:', max_capacity)
            if crates_needed > max_capacity:
                capacity_exceeded = True
                message = "Total driver capacity: {}, total crates: {}. Add more drivers or increase capacity".format(
                    max_capacity, crates_needed)
            elif (max_capacity - crates_needed) > 15:
                capacity_exceeded = False
                message = "Total driver capacity: {}, total crates: {}. Consider removing a operator".format(
                    max_capacity, crates_needed)
            else:
                capacity_exceeded = False
                message = False
            return capacity_exceeded, message
