from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('artist', 'title', 'price', 'year', 'author', 'created_at')
    list_filter = ('artist', 'year', 'author')
    search_fields = ('artist', 'title')
    # readonly_field = ('created_at')

    fieldsets = (
        ('Основаная информация', {
            'fields': ('artist', 'title', 'year', 'price')
            }),
            ('Дполнительно', {
                'fields': ('cover_url', 'description', 'author')
            }),
            # ('Системные поля', {
            #      'fields': ('created_at',),
            #      'classes': ('collapse',)
            # })
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'album', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('text', 'author__username', 'album__title')
    readonly_fields = ('created_at', 'updated_at')