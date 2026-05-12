from django.contrib import admin
from .models import *
from django.db.models import Count, Avg, Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse
# Register your models here.

# class AlbumImageInLine(admin.TabularInline):
#     model = Album
#     fields = ('cover_image', 'cover_url')
#     readonly_fields = ('cover_image',)
#     extra = 0
#     can_delete = False
#     max_num = 1

# @admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'artist', 'title', 'price', 'year', 'author', 'views')
    list_display_links = ('id',  'artist', 'title')
    list_filter = ('artist', 'year', 'author')
    search_fields = ('artist', 'title', 'description', 'author__username')
    readonly_field = ('created_at', 'updated_at') 

    fieldsets = (
                ('Основаная информация', {
                    'fields': ('artist', 'title', 'year', 'price', 'description')
                    }),
                ('Визуальное оформление', {
                    'fields': ('cover_image', 'cover_url'),
                    'classes': ('collapse',)
                }),
                ('Авторство и статистика',{
                    'fields': ('author', 'views', ),
                    'classes': ('wide','extrapretty')
                })
                # ('Дополнительно', {
                #     'fields': ('cover_url', 'description', 'author')
                # }),
            # ('Системные поля', {
            #      'fields': ('created_at',),
            #      'classes': ('collapse',)
            # })
    )
    # inlines = [AlbumImageInLine]

    actions = ['increase_views', 'export_to_csv']


    # def cover_preview(self, obj):
    #     if obj.cover_image:
    #         return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.cover_image.url)
    #     elif obj.cover_url:
    #         return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.cover_url)
    #     return format_html('<div style="width: 100px; height: 100px; background-color: #eee; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;">Нет изображения</div>')
    # cover_preview.short_description = 'Обложка'

    def increase_views(self, request, queryset):
        for album in queryset:
            album.views += 100
            album.save()
        self.message_user(request, f"Просмотры увеличены на 100 для {queryset.count()} альбомов")

    increase_views.short_description = "Увеличить просмотры на 100"

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="albums_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'artist', 'title', 'year', 'price', 'description', 'cover_url', 'author', 'views', 'created_at', 'updated_at'])

        for album in queryset:
            writer.writerow([album.id, album.artist, album.title, album.year, album.price, album.description, album.cover_url, album.author, album.views, album.created_at, album.updated_at])

        return response

    export_to_csv.short_description = "Экспорт в CSV"


# @admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('id','short_text', 'album_link','author_link', 'created_at_short')
    list_filter = ('author', 'created_at')
    search_fields = ('text', 'author__username', 'album__title')
    readonly_fields = ('created_at', 'updated_at')

    def short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    short_text.short_description = 'Текст комментария'

    def album_link(self, obj):
        url = reverse('admin:catalog_album_change', args=[obj.album.id])
        return format_html('<a href="{}">{}</a>', url, obj.album.title)
    album_link.short_description = 'Альбом'

    def author_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Автор'

    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_short.short_description = 'Дата создания'


    actions = ['delete_selected_comments']

    def delete_selected_comments(self, request, queryset):
        queryset.delete()
        self.message_user(request, f"Выбранные комментарии удалены")
    delete_selected_comments.short_description = "Удалить выбранные комментарии"


class CartItemInLine(admin.TabularInline):
    model = CartItem
    fields = ['album', 'quantity', 'get_total_price']
    extra = 0
    can_delete = True

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = 'Итого'


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info','get_total_items', 'get_total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def user_info(self, obj):
        return f'{obj.user.username} ({obj.user.email})'
    user_info.short_description = 'Пользователь'
    
    inlines = [CartItemInLine]

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Количество товаров'

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Итого'



class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    fields = ('album', 'quantity', 'get_total_price')
    extra = 0
    can_delete = True
    readonly_fields = ('get_total_price',)

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Итого'


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('id', 'user_info', 'get_total_items', 'total_price', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'phone', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInLine]
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user',  'status','total_price'),
        }),
        ('Данные для доставки',{
            'fields': ('shipping_address', 'phone','comment'),
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)}
        )
    )

    def user_info(self, obj):
        return f'{obj.user.username} ({obj.user.email})'
    user_info.short_description = 'Пользователь'


    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Количество товаров'

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Итого'

    actions = ['mark_as_pending', 'mark_as_processing', 'mark_as_shipped',
                'mark_as_delivered', 'mark_as_cancelled', 'export_orders_csv']

    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, f"Выбранные заказы помечены как 'pending'")
    mark_as_pending.short_description = "Пометить выбранные заказы как 'pending'"

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"Выбранные заказы помечены как 'processing'")
    mark_as_processing.short_description = "Пометить выбранные заказы как 'processing'"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"Выбранные заказы помечены как 'shipped'")
    mark_as_shipped.short_description = "Пометить выбранные заказы как 'shipped'"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"Выбранные заказы помечены как 'delivered'")
    mark_as_delivered.short_description = "Пометить выбранные заказы как 'delivered'"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"Выбранные заказы помечены как 'cancelled'")
    mark_as_cancelled.short_description = "Пометить выбранные заказы как 'cancelled'"

    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'user', 'status', 'total_price', 'shipping_address', 'phone', 'comment', 'created_at', 'updated_at'])

        for order in queryset:
            writer.writerow([order.id, order.user, order.status, order.total_price, order.shipping_address, order.phone, order.comment, order.created_at, order.updated_at])

        return response

    export_orders_csv.short_description = "Экспортировать выбранные заказы в CSV"


admin.site.register(Album, AlbumAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Cart, CartAdmin)
# admin.site.register(CartItem, CartItemInLine)
admin.site.register(Order, OrderAdmin)