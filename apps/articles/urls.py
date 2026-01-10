from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, CategoryViewSet, CommentViewSet, TagViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    # Nested comments under articles
    path(
        'articles/<slug:article_slug>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='article-comments'
    ),
    path(
        'articles/<slug:article_slug>/comments/<int:pk>/',
        CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='article-comment-detail'
    ),
]
