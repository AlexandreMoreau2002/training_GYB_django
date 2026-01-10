from django.db import models
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Article, Category, Comment, Tag
from .serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    CategorySerializer,
    CommentCreateSerializer,
    CommentSerializer,
    TagSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing categories."""

    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.annotate(
            articles_count=Count('articles', filter=models.Q(articles__status='published'))
        ).order_by('name')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for articles with full CRUD."""

    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'status', 'author__username']
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['created_at', 'published_at', 'title']
    ordering = ['-published_at']

    def get_queryset(self):
        queryset = Article.objects.select_related(
            'author', 'author__profile', 'category'
        ).prefetch_related('tags').annotate(
            comments_count=Count('comments')
        )

        # Non-authenticated users only see published articles
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        # Authenticated users see published + their own drafts
        elif not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(status='published') | models.Q(author=self.request.user)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Only author or staff can update
        if self.get_object().author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres articles.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only author or staff can delete
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres articles.")
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments on an article."""

    serializer_class = CommentSerializer

    def get_queryset(self):
        article_slug = self.kwargs.get('article_slug')
        return Comment.objects.filter(
            article__slug=article_slug
        ).select_related('author', 'author__profile').order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        article_slug = self.kwargs.get('article_slug')
        try:
            article = Article.objects.get(slug=article_slug)
            context['article_id'] = article.id
        except Article.DoesNotExist:
            pass
        return context

    def perform_create(self, serializer):
        article_slug = self.kwargs.get('article_slug')
        article = Article.objects.get(slug=article_slug)
        serializer.save(author=self.request.user, article=article)

    def perform_update(self, serializer):
        if self.get_object().author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres commentaires.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres commentaires.")
        instance.delete()
