from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Album, Comment, Cart, CartItem, Order, OrderItem
from .export_services import *
from .forms import AlbumForm, CommentForm, OrderForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from django.http import JsonResponse
from .export_services import StatisticsService
import json
# Create your views here.


def album_list(request):
    albums = Album.objects.all()
    return render(request, 'catalog/album_list.html', {'page_obj': albums,})


def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    album.views += 1

    album.save()

    return render(request, 'catalog/album_detail.html', {'album': album})

@login_required
def album_create(request):
    print('check valid')
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            album.author = request.user
            album.save()
            messages.success(request, f'Альбом "{album.artist} - {album.title}" успешно добавлен!')
            return redirect('album_detail', pk=album.pk)
    else:
        form = AlbumForm()
    
    return render(request, 'catalog/album_form.html', {'form': form, 'action': 'create'})



@login_required
def album_delete(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if album.author != request.user and not request.user.is_superuser:
        messages.error(request, 'У Вас нет прав на удаление этого альбома.')
        return redirect('album_detail', pk=pk)
    
    if request.method == 'POST':
        album_title = f"{album.artist} - {album.title}"
        album.delete()
        messages.success(request, f'Альбом "{album_title}"  успешно удален!')
        return redirect('album_list')
    
    return render(request, 'catalog/album_confirm_delete.html', {'album': album})


@login_required
def album_edit(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if album.author != request.user and not request.user.is_superuser:
        messages.error(request, 'У Вас нет прав на редактирование этого альбома.')
        return redirect('album_detail', pk=pk)
    
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, instance=album)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, f'Альбом "{album.artist} - {album.title}" успешно обновлен!')
            return redirect('album_detail', pk=album.pk)
    else:
        form = AlbumForm(instance=album)
    
    return render(request, 'catalog/album_form.html', {
        'form': form,
        'action': 'edit',
        'album': album
        })


@login_required
def comment_create(request, album_pk):
    album = get_object_or_404(Album, pk=album_pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.album = album
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
    
    return redirect('album_detail', pk=album_pk)


@login_required
def comment_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    # Проверяем права на удаление
    if comment.author != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы не можете удалить чужой комментарий!')
        return redirect('album_detail', pk=comment.album.pk)
    
    album_pk = comment.album.pk
    comment.delete()
    messages.success(request, 'Комментарий удален!')
    
    return redirect('album_detail', pk=album_pk)


@login_required
def cart_view(request):
    cart = request.cart
    return render(request, 'catalog/cart.html', {'cart': cart})


@require_POST
def cart_remove(request, item_id):
    cart = request.cart
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    album_title = cart_item.album.title
    cart_item.delete()
    messages.success(request, f'Товар "{album_title}" удален из корзины!')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': request.cart.get_total_items(),
            'total_price': request.cart.get_total_price()
            })
    return redirect('cart_view')


@require_POST
def add_cart(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    cart = request.cart

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        album=album,
        defaults={'quantity': quantity},
    )

    if not created:
        cart_item.quantity = quantity
        cart_item.save()

    messages.success(request, f'"{album.title}" добавлен в корзину.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': request.cart.get_total_items(),
            'total_price': request.cart.get_total_price(),
            'item_total': cart_item.get_total_price(),
        })
    return redirect('cart_view')

@require_POST
def cart_update(request, item_id):
    """Обновление количества товара в корзине"""
    cart = getattr(request, 'cart', None)
    if not cart:
        return redirect('cart_view')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    messages.success(request, 'Корзина обновлена')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_price': str(cart.get_total_price()),
            'item_total': str(cart_item.get_total_price()) if quantity > 0 else '0'
        })
    
    return redirect('cart_view')


@login_required
def checkout_view(request):
    cart = request.cart

    if cart.get_total_items() == 0:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect("cart_view")
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price(),
                shipping_address=form.cleaned_data['shipping_address'],
                phone=form.cleaned_data['phone'],
                comment=form.cleaned_data['comment'],
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    album=cart_item.album,
                    quantity=cart_item.quantity,
                    price=cart_item.album.price,
                )
            cart.clear()

            messages.success(request, f"Заказ №{order.id} успешно оформлен.")
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'catalog/checkout.html', {
        'form': form,
        'cart': cart
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'catalog/order_detail.html', {'order': order})


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'catalog/orders_list.html', {'orders': orders})



### Staff required


@staff_member_required
def export_orders_excel(request):
    orders = Order.objects.all().select_related('user').prefetch_related("order_items__album")
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')


    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    if status:
        orders = orders.filter(status=status)

    filename = f"orders_export_{datetime.now().strftime("%Y%m%d_%H:%M")}.xlsx"
    return ExportService.export_orders_to_excel(orders, filename)


@staff_member_required
def export_orders_csv(request):
    orders = Order.objects.all().select_related('user').prefetch_related("order_items__album")
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')


    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    if status:
        orders = orders.filter(status=status)

    filename = f"orders_export_{datetime.now().strftime("%Y%m%d_%H:%M")}.csv"
    return ExportService.export_orders_to_csv(orders, filename)


@staff_member_required
def export_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return ExportService.export_order_to_pdf(order)


@staff_member_required
def export_orders_pdf(request):
    orders = Order.objects.all().select_related('user').prefetch_related("order_items__album")
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')


    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    if status:
        orders = orders.filter(status=status)

    filename = f"orders_export_{datetime.now().strftime("%Y%m%d_%H:%M")}.pdf"
    return ExportService.export_orders_to_pdf(orders, filename)


@staff_member_required
def statistics_dashboard(request):

    days = int(request.GET.get('days', 30))
    
    # Собираем статистику
    daily_stats = StatisticsService.get_daily_stats(days)
    top_albums = StatisticsService.get_top_albums(10)
    top_users = StatisticsService.get_top_users(10)
    status_stats = StatisticsService.get_status_stats()
    monthly_revenue = StatisticsService.get_monthly_revenue()
    
    # Общая статистика
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=models.Sum('total_price'))['total'] or 0
    total_users = User.objects.count()
    total_albums = Album.objects.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Конвертируем в JSON для JavaScript
    context = {
        'daily_stats': daily_stats,
        'top_albums': top_albums,
        'top_users': top_users,
        'status_stats': json.dumps(status_stats),
        'monthly_revenue': json.dumps(monthly_revenue),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'total_albums': total_albums,
        'avg_order_value': avg_order_value,
        'selected_days': days,
    }
    
    return render(request, 'catalog/statistics_dashboard.html', context)


