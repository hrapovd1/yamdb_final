from api.validators import validate_username
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей."""
    username = serializers.CharField(
        max_length=settings.FIELDS_LENGTH['USERNAME'],
        validators=[
            validate_username,
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        max_length=settings.FIELDS_LENGTH['EMAIL'],
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        ]
        lookup_field = 'username'


class RegisterSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователей."""
    username = serializers.CharField(
        label="Username",
        required=True,
        max_length=settings.FIELDS_LENGTH['USERNAME'],
        validators=[validate_username]
    )
    email = serializers.EmailField(
        max_length=settings.FIELDS_LENGTH['EMAIL'],
        required=True
    )


class AuthTokenSerializer(serializers.Serializer):
    """Сериализатор для токенов."""
    username = serializers.CharField(
        label="Username",
        required=True
    )
    confirmation_code = serializers.CharField(
        label="Confirmation code",
        trim_whitespace=False,
        required=True
    )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        user = self.context['request'].user
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                "Нельзя добавить второй отзыв на то же самое произведение"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review', 'author', 'pub_date')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""
    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""
    class Meta:
        exclude = ['id']
        model = Genre


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, редактирования и удаления произведений."""
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(source='reviews__score__avg',
                                    read_only=True)

    class Meta:
        fields = '__all__'
        model = Title
