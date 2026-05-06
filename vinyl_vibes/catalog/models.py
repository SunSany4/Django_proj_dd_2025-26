from django.db import models
from django.contrib.auth.models import User
import os 
from decimal import Decimal
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



class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        if self.user:
            return f"Корзина {self.user.username}"
        return f"Корзина (сессия: {self.user.username})"
    
    def get_total_price(self):
        total = sum(item.get_total_price() for item in self.items.all())
        return total
    
    def get_total_items(self):
        quantity = sum(item.quantity for item in self.items.all())
        return  quantity
    
    def clear(self):
        self.items.all().delete()

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'



class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
        )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.album.title} x {self.quantity}"
    
    def get_total_price(self):
        return self.album.price * self.quantity
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        # unique_together = ['cart', 'album']


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', "Ожидает обработки"),
        ('processing', "В обработке"),
        ('shipped', "Отправлен"),
        ('delivered', "Доставлен"),
        ('cancelled', "Отменен"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    items = models.ManyToManyField(Album, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(verbose_name="Адрес доставки")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    comment = models.TextField(blank=True, verbose_name='Коммнетарий к заказу')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.album.title} x {self.quantity}"
    
    def get_total_price(self):
        return self.price * self.quantity