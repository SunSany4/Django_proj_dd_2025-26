# -*- coding: utf-8 -*-

import csv
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
import io
import csv
import openpyxl
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ExportService:
    # def export_orders_to_excel(orders, filename):
    #     pass

    # def export_orders_to_csv(orders, filename):
    #     pass

    # def export_order_to_pdf(order):
    #     pass

    @staticmethod
    def get_additional_stats(orders):
        stats = orders.aggregate(
            total_orders=models.Count('id'),
            total_revenue=models.functions.Coalesce(
                models.Sum('total_price', output_field=models.DecimalField(max_digits=10)),
                models.Value(0, output_field=models.DecimalField(max_digits=2))),
            total_items=models.Sum('order_items__quantity', output_field=models.DecimalField(max_digits=10)),
            total_positions=models.Count('order_items', distinct=True),
            unique_users=models.Count('user', distinct=True)
        )
        status_stats = orders.values('status').annotate(
            count=models.Count('id', output_field=models.IntegerField()),
            total_amount=models.Sum('total_price', output_field=models.DecimalField(max_digits=20)),
            avg_amount=models.functions.Coalesce(
                models.Sum('total_price', output_field=models.DecimalField(max_digits=20)) / models.Count('id',
                                                                                                          output_field=models.DecimalField(
                                                                                                              max_digits=20)),
                models.Value(0, output_field=models.DecimalField(max_digits=20)))
        ).order_by('-count')
        total_orders = orders.count()
        return stats, status_stats, total_orders

    @staticmethod
    def export_orders_to_excel(orders, filename):
        

        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Статистика по заказам'

        stats, status_stats, total_orders = ExportService.get_additional_stats(orders)
        print(stats)
        ws.append(['Количество заказов', stats['total_orders']])
        ws.append(['Прибыль', f'{stats['total_revenue']:.2f}' + u' ₽'])
        ws.append(['Общее количество товаров в заказах', stats['total_items'] or 0])
        ws.append(['Позиций', stats['total_positions']])
        ws.append(['Пользователи', stats['unique_users']])
        ws.append([])
        ws.append(['Средний чек', f"{stats['total_revenue'] / stats['total_orders']:.2f} ₽" if stats['total_orders'] > 0 else 0])
        ws.append(['Среднее количество товаров на заказ', f"{stats['total_items'] / stats['total_orders']:.1f}" if stats['total_orders'] > 0 and stats['total_items'] is not None else 0])

        ws.append([])
        ws.append(['СТАТИСТИКА ПО СТАТУСАМ'])
        ws.append(['Статус', 'Количество', 'Сумма', 'Средний чек', '% от общего'])
        for stat in status_stats:
            status_label = dict(Order.STATUS_CHOICES).get(stat['status'], stat['status'])
            percentage = (stat['count'] / total_orders * 100) if total_orders > 0 else 0

            ws.append([
                status_label,
                stat['count'],
                f"{stat['total_amount'] or 0:.2f}",
                f"{stat['avg_amount']:.2f}",
                f"{percentage:.1f}"
            ])

        ws.append([])
        ws.append(['Детальный список заказов'])
        ws.append(['ID заказа', 'Пользователь', 'Статус', 'Сумма',
                   'Количество заказов', 'Количество позиций',
                   'Телефон', 'Дата создания'])
        orders_detail = orders.select_related('user').prefetch_related('order_items')
        for order in orders_detail:
            ws.append([
                order.id,
                f"{order.user}",
                order.get_status_display(),
                f"{order.total_price:.2f}",
                order.get_total_items(),
                order.get_items_count(),
                order.phone,
                order.created_at.strftime('%d.%m.%Y %H:%M')
            ])

        ExportService._apply_styles(ws)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

    @staticmethod
    def _apply_styles(ws):
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    len_cell_value = len(str(cell.value))
                    if len_cell_value > max_length:
                        max_length = len_cell_value
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    @staticmethod
    def export_orders_to_csv(orders, filename):
        # with open(filename, 'w', newline='', encoding='utf-8') as file:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(['Статистика по заказам'])
        stats, status_stats, total_orders = ExportService.get_additional_stats(orders)
        writer.writerow(['Количество заказов', stats['total_orders']])
        writer.writerow(['Прибыль', f'{stats['total_revenue']:.2f} ₽'])
        writer.writerow(['Общее количество товаров в заказах', stats['total_items'] or 0])
        writer.writerow(['Позиций', stats['total_positions']])
        writer.writerow(['Пользователи', stats['unique_users']])
        writer.writerow([])
        writer.writerow(['Средний чек',
                    f"{stats['total_revenue'] / stats['total_orders']:.2f} ₽" if stats['total_orders'] > 0 else 0])
        writer.writerow(['Среднее количество товаров на заказ',
                    f"{stats['total_items'] / stats['total_orders']:.1f}" if stats['total_orders'] > 0 and stats[
                        'total_items'] is not None else 0])

        writer.writerow([])
        writer.writerow(['СТАТИСТИКА ПО СТАТУСАМ'])
        writer.writerow(['Статус', 'Количество', 'Сумма', 'Средний чек', '% от общего'])
        for stat in status_stats:
            status_label = dict(Order.STATUS_CHOICES).get(stat['status'], stat['status'])
            percentage = (stat['count'] / total_orders * 100) if total_orders > 0 else 0

            writer.writerow([
                status_label,
            stat['count'],
            f"{stat['total_amount'] or 0:.2f}",
            f"{stat['avg_amount']:.2f}",
            f"{percentage:.1f}"
        ])

        writer.writerow([])
        writer.writerow(['Детальный список заказов'])
        writer.writerow(['ID заказа', 'Пользователь', 'Статус', 'Сумма',
                    'Количество заказов', 'Количество позиций',
                    'Телефон', 'Дата создания'])
        orders_detail = orders.select_related('user').prefetch_related('order_items')
        for order in orders_detail:
            writer.writerow([
                order.id,
                f"{order.user}",
                order.get_status_display(),
                f"{order.total_price:.2f}",
                order.get_total_items(),
                order.get_items_count(),
                order.phone,
                order.created_at.strftime('%d.%m.%Y %H:%M')
            ])

        
        return response

    @staticmethod
    def export_orders_to_pdf(orders, filename):
        def ru_paragraph(text):
            return Paragraph(text, cyrillic_style)
        
       
                

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        stats, status_stats, total_orders = ExportService.get_additional_stats(orders)
        pdfmetrics.registerFont(TTFont('Roboto', 'Roboto-Regular.ttf'))

        styles = getSampleStyleSheet()
        cyrillic_style = ParagraphStyle(
                                        'CyrillicStyle',
                                        parent=styles['Normal'],
                                        fontName='Roboto',
                                        fontSize=14
)


        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        story = []
        title = ru_paragraph('Отчёт по заказам')
        story.append(title)
        story.append(Spacer(1, 0.2))

        story.append(ru_paragraph('Общая статистика'))

        stats_data = [
            ['Показатель', 'Значение'],
            ['Количество заказов', str(stats['total_orders'])],
            ['Прибыль', f"{stats['total_revenue']:.2f} ₽"],
            ['Общее количество товаров в заказах', str(stats['total_items'] or 0)],
            ['Позиций', str(stats['total_positions'])],
            ['Пользователи', str(stats['unique_users'])],
            ['Средний чек',
             f"{stats['total_revenue'] / stats['total_orders']:.2f} ₽" if stats['total_orders'] > 0 else 0],
            ['Среднее количество товаров на заказ',
             (f"{stats['total_items'] / stats['total_orders']:.1f}" if stats['total_orders'] > 0 and
             stats['total_items'] is not None else 0)]
        ]
        stats_table = Table(stats_data, colWidths=[200, 150])
        stats_table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Roboto')]))
            
        story.append(stats_table)

        story.append(ru_paragraph("Статистика по статусам"))
        status_data = [['Статус', 'Количество', 'Сумма', 'Средний чек', '% от общего']]
        for stat in status_stats:
            status_label = dict(Order.STATUS_CHOICES).get(stat['status'], stat['status'])
            percentage = (stat['count'] / total_orders * 100) if total_orders > 0 else 0

            status_data.append([
                status_label,
                str(stat['count']),
                f"{stat['total_amount'] or 0:.2f}",
                f"{stat['avg_amount']:.2f}",
                f"{percentage:.1f}"
            ])

        status_table = Table(status_data, colWidths=[100, 80, 100, 100, 80])
        status_table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Roboto')]))
        story.append(status_table)
        story.append(Spacer(1, 0.2))

        story.append(ru_paragraph("Детальный список заказов"))
        orders_data = [['ID', 'Пользователь', "Статус", "Сумма", "Количество заказов", "Позиций", "Телефон", "Дата создания"]]
        orders_detail = orders.select_related('user').prefetch_related('order_items')
        for order in orders_detail:
            orders_data.append([
                str(order.id),
                f"{order.user}",
                order.get_status_display(),
                f"{order.total_price:.2f}",
                str(order.get_total_items()),
                str(order.get_items_count()),
                order.phone,
                order.created_at.strftime('%d.%m.%Y %H:%M')
            ])

        orders_table = Table(orders_data, repeatRows=1)
        orders_table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Roboto')]))
        story.append(orders_table)
        doc.build(story)
        return response


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

