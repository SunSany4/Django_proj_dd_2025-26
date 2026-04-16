from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Album, Comment
from .serializers import (AlbumSerializer, CommentSerializer, AlbumDetailSerializer, UserSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import IsAuthorOrReadonly




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