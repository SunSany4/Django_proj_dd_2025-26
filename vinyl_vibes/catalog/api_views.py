from rest_framework import viewsets, generics, permissions, filters, status
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import IsAuthorOrReadonly
from django_filters.rest_framework import DjangoFilterBackend




class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadonly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['artist',  'year', 'author__username']
    search_fields = ['title', 'artist', 'description']
    ordering_fields = ['price', 'year', 'created_at', 'views']
    orderind = ['-created_at']


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlbumDetailSerializer
        return AlbumSerializer
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        album = self.get_object()
        album.views += 1
        album.save()
    
        return Response({'views': album.views}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def add_coment(self, request, pk=None):
        album = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(album=album, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'])
    def my_albums(self, request):
        user = request.user
        albums = Album.objects.filter(author=user)
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadonly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    
    def qet_queryset(self):
        queryset = super().get_queryset()
        album_id = self.request.query_params.get('album_id')
        if album_id:
            return queryset.filter(album_id=album_id)
        return queryset



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadonly]



class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })
    

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.filter(session_key=self.request.session.session_key)
    
    @action(detail=False, methods='get')
    def my_cart(self, request):
        serializer = self.get_serializer(request.cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        album_id = request.data.get('album_id')
        quantity = int(request.data.get('quantity', 1))

        album = get_object_or_404(Album, id=album_id)
        cart = request.cart

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            album=album,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        album_id = request.data.get('album_id')
        quantity = int(request.data.get('quantity', 1))

        cart_item = get_object_or_404(CartItem, id=album_id, cart=request.cart)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        item_id = request.data.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart=request.cart)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=False, methods=['post'])
    def clear(self, request):
        request.cart.clear()
        return Response({'message': 'Корзина очищена.'})



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        cart = self.request.cart

        if cart.get_total_items() == 0:
            raise serializers.ValidationError("Ваша корзина пуста.")

        order = serializer.save(
            total_price=cart.get_total_price(),
            user=self.request.user
            )
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                album=cart_item.album,
                quantity=cart_item.quantity,
                price=cart_item.price,
            )
        cart.clear()
        return order