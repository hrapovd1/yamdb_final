from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsModeratorOrOwnerOrReadOnly)
from api.serializers import (AuthTokenSerializer, CategorySerializer,
                             CommentSerializer, GenreSerializer,
                             RegisterSerializer, ReviewSerializer,
                             TitleGetSerializer, TitleWriteSerializer,
                             UserSerializer)
from api.utils import get_random_string
from reviews.models import Category, Genre, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для доступа к пользователям."""
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    lookup_value_regex = '[^/.]+'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if (
            self.queryset.filter(email=email).exists()
            or self.queryset.filter(username=username).exists()
        ):
            return Response(
                {'Такой email существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user)
        if self.action == 'patch':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                if not user.is_admin and 'role' in serializer.validated_data:
                    serializer.validated_data.pop('role')
                serializer.save(**serializer.validated_data)
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )


class AuthView(APIView):
    """View класс для создания пользователя."""
    permission_classes = [permissions.AllowAny]

    def send_email(self, user: User) -> Response:
        email_body = (
            'Ваш код подтверждения: {code} \n'.format(
                code=user.confirmation_code
            )
            + 'Получить токен можно через POST запрос, с телом запроса:\n'
            + '    {\n'
            + '      "username": "{name}",\n'.format(name=user.username)
            + '      "confirmation_code": "{code}"\n'.format(
                code=user.confirmation_code
            )
            + '    }\n'
            + 'на url /api/v1/auth/token/\n'
        )
        send_mail(
            'Confirmation code from Django',
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            (user.email,)
        )
        return Response(
            {
                'username': user.username,
                'email': user.email
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Предложенный в ревью вариант использования try/except
            # не проходит тест при использовании уже существующего
            # email, пользователь успешно создается, оставил свой вариант.
            user_exists = User.objects.filter(
                username=serializer.validated_data['username']
            ).exists()
            email_exists = User.objects.filter(
                email=serializer.validated_data['email']
            ).exists()
            if user_exists ^ email_exists:
                return Response(
                    'Не корректные данные.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif user_exists and email_exists:
                user = get_object_or_404(
                    User,
                    username=request.data['username'])
                return self.send_email(user)

            user = User.objects.create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
            confirmation_code = get_random_string()
            user.confirmation_code = confirmation_code
            user.save()
            return self.send_email(user)

        if serializer.errors:
            error = serializer.errors
        else:
            error = 'Не корректные данные.'
        return Response(
            error,
            status=status.HTTP_400_BAD_REQUEST
        )


class AuthTokenView(APIView):
    """View класс для получения токена."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, username=serializer.validated_data.get('username')
            )
            if user.confirmation_code == serializer.validated_data.get(
                'confirmation_code'
            ):
                refresh = RefreshToken.for_user(user)
                return Response(
                    {'token': str(refresh.access_token)},
                    status=status.HTTP_200_OK
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    Возвращает список всех комментариев к ревью.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsModeratorOrOwnerOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Возвращает список всех отзывов.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsModeratorOrOwnerOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    """ViewSet для доступа к категориям."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """ViewSet для доступа к жанрам."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для доступа к произведениям."""
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return TitleGetSerializer
        return TitleWriteSerializer
