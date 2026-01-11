from django.urls import path, include
from .views import MeView, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user') 
# Note: Since this urls.py is likely included via 'api/users/', registering with '' will make it 'api/users/'.
# However, to avoid conflict with 'me/', we should check how it is included in the project urls.
# Usually apps have their own namespace. Let's assume we want 'api/users/' for the list.
# But 'me/' is already there. 
# If I use router.register(r'', ...), it handles the root. 'me/' is a separate path.
# Let's verify project structure but usually:
# path('users/', include('apps.users.urls')) -> 'api/users/me/' works.
# If I add router, 'api/users/' will list users.

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
