from rest_framework import serializers

from apps.users.serializers import UserMinimalSerializer

from .models import Article, Category, Comment, Tag


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    articles_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'articles_count']
        read_only_fields = ['slug']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with nested replies."""

    author = UserMinimalSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'parent',
            'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        # Only get replies for root comments (parent=None)
        if obj.parent is None:
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""

    class Meta:
        model = Comment
        fields = ['content', 'parent']

    def validate_parent(self, value):
        if value and value.article_id != self.context.get('article_id'):
            raise serializers.ValidationError(
                "Le commentaire parent doit appartenir au même article."
            )
        return value


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for article list (minimal data)."""

    author = UserMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'image_url',
            'author', 'category', 'tags', 'status',
            'created_at', 'published_at', 'comments_count'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for article detail (full data)."""

    author = UserMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'image_url',
            'author', 'category', 'tags', 'status',
            'created_at', 'updated_at', 'published_at',
            'comments', 'comments_count'
        ]

    def get_comments(self, obj):
        # Only root comments (replies are nested inside)
        root_comments = obj.comments.filter(parent=None)
        return CommentSerializer(root_comments, many=True).data


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating articles."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Article
        fields = [
            'title', 'excerpt', 'content', 'image_url',
            'category', 'tags', 'status'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
