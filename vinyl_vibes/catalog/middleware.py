from .models import Cart, CartItem

class CartMiddleware:
    # def __init__(self, get_response):
    #     self.get_response = get_response
        

    # def __call__(self, request):
    #     if request.user.is_authenticated:
    #         cart, created = Cart.objects.get_or_create(user=request.user)

    #         if request.session.get('cart_id') and not created:
    #             old_cart_id = request.session.get('cart_id')
    #             try:
    #                 old_cart = Cart.objects.get(id=old_cart_id, session_key=request.session.session_key)
    #                 for item in old_cart.items.all():
    #                     cart_item, created = CartItem.objects.get_or_create(
    #                         cart=cart,
    #                         album=item.album,
    #                         defaults={'quantity': item.quantity},
    #                     )
    #                     if not created:
    #                         cart_item.quantity += item.quantity
    #                         cart_item.save()

    #                 old_cart.delete()
    #             except Cart.DoesNotExist:
    #                 pass
    #         request.cart = cart
    #     else:
    #         if not request.session.session_key:
    #             request.session.create()
            
    #         session_key = request.session.session_key
    #         cart, created = Cart.objects.get_or_create(
    #             session_key=session_key,
    #             user=None
    #         )
    #     request.session['cart_id'] = request.cart.id
    #     response = self.get_response(request)
    #     return response
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Создаем или получаем корзину для пользователя
        cart = None
        
        if request.user.is_authenticated:
            # Для авторизованных пользователей
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Если есть корзина с session_key, переносим товары
            session_cart_id = request.session.get('cart_id')
            if session_cart_id and not created:
                try:
                    old_cart = Cart.objects.get(id=session_cart_id, session_key=request.session.session_key, user=None)
                    if old_cart and old_cart.id != cart.id:
                        for item in old_cart.items.all():
                            cart_item, created = CartItem.objects.get_or_create(
                                cart=cart,
                                album=item.album,
                                defaults={'quantity': item.quantity}
                            )
                            if not created:
                                cart_item.quantity += item.quantity
                                cart_item.save()
                        old_cart.delete()
                except Cart.DoesNotExist:
                    pass
            
            # Удаляем session_key если была
            cart.session_key = None
            cart.save()
            
        else:
            # Для неавторизованных - используем сессию
            if not request.session.session_key:
                request.session.create()
            
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                user=None
            )
        
        # Привязываем корзину к запросу
        request.cart = cart
        
        # Сохраняем ID корзины в сессии
        request.session['cart_id'] = cart.id
        
        response = self.get_response(request)
        return response