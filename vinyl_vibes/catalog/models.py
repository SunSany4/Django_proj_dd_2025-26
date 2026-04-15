from django.db import models
from django.contrib.auth.models import User
import os 
# Create your models here.


def upload_cover_path(instance, filename):
   ext = filename.split('.')[-1]
   filename = f"{instance.artist}_{instance.title}_{instance.pk}.{ext}"
   return os.path.join('covers', filename)


class Album(models.Model):

    title = models.CharField(max_length=200, verbose_name="Название альбома")
    artist = models.CharField(max_length=200, verbose_name="Исполнитель")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    cover_image = models.ImageField(
        upload_to=upload_cover_path,
        verbose_name="Обложка (файл)",
        blank=True,
        null=True,
    )
    cover_url = models.URLField(verbose_name="URL обложки", blank=True)
    description = models.TextField(verbose_name="Описание",blank=True)
    year = models.IntegerField(verbose_name="Год выпуска", blank=True, null=True)
    author = models.ForeignKey(
        User,
        on_delete = models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Автор",
        related_name='Albums',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    def get_cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_url


    def __str__(self):
        return f"{self.artist} - {self.title}"
    
    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"
        ordering = ['-created_at']
        



class Comment(models.Model):
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Альбом"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.album.title}"
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']