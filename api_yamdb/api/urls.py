from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (AuthTokenView, AuthView, CategoryViewSet,
                       CommentViewSet, GenreViewSet, ReviewViewSet,
                       TitleViewSet, UserViewSet)

v1_router = SimpleRouter()
v1_router.register(
    r'titles/(?P<title_id>[^/.]+)/reviews',
    ReviewViewSet,
    basename='review'
)
v1_router.register(
    r'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    CommentViewSet,
    basename='comment'
)
v1_router.register('users', UserViewSet, basename='user')
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('titles', TitleViewSet, basename='title')


urlpatterns = [
    path('v1/auth/signup/', AuthView.as_view()),
    path('v1/auth/token/', AuthTokenView.as_view()),
    path('v1/', include(v1_router.urls)),
]
