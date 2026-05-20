import csv
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
import io



class ExportService:
    def export_orders_to_excel(orders, filename):
        pass

    def export_orders_to_csv(orders, filename):
        pass

    def export_order_to_pdf(order):
        pass
    


class StatisticsService:

    def get_daily_stats(days=30):
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        daily_stats = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)

            orders = Order.objects.filter(created_at__gte=date, created_at__lt=next_date)
            daily_stats.append({
                'date': date.strftime('%d.%m'),
                'orders_count': orders.count(),
                'revenue': float(sum(order.total_price for order in orders)),
                'avg_order_value': float(sum(order.total_price for order in orders) / orders.count()) if orders else 0
            })
            print(daily_stats, days, sep='\n')
        return daily_stats
        


    def get_top_albums(nums=10):
        pass

    def get_top_users(nums=10):
        pass
    
    def get_status_stats():
        pass

    def get_monthly_revenue():
        pass

