from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Album, Comment, Cart, CartItem, Order, OrderItem
from .forms import AlbumForm, CommentForm, OrderForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'catalog/order_detail.html', {'order': order})


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'catalog/orders_list.html', {'orders': orders})


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


#TODO: оформление заказа
#TODO: обновление количества товаров
#TODO: добавление товара в корзину
