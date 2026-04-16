from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Album, Comment



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']



class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    class Meta:
        model = Comment
        fields = ['author_id', 'author_name', 'text', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    

class AlbumSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    comment_count = serializers.SerializerMethodField()
    cover_url_display = serializers.SerializerMethodField()


    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'price', 'cover_image', 'cover_url',
                   'description', 'year', 'author_name', 'author_id', 'views', 
                   'created_at', 'updated_at', 'comment_count', 'cover_url_display']
        read_only_fields = ['author', 'created_at', 'updated_at', 'views']
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_cover_url_display(self, obj):
        if obj.cover_url:
            return obj.cover_url
        elif obj.cover_image:
            return obj.cover_image.url
        else:
            return None
        

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    


class AlbumDetailSerializer(AlbumSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(AlbumSerializer.Meta):
        fields = AlbumSerializer.Meta.fields + ['comments']