import datetime as dt

from api.validators import validate_username
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MAX_STR_LENGTH: int = 30


class User(AbstractUser):
    """Расширенная модель для пользователей."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        choices=ROLES,
        default=USER,
        max_length=15
    )
    username = models.CharField(
        max_length=settings.FIELDS_LENGTH['USERNAME'],
        unique=True,
        validators=[validate_username]
    )
    confirmation_code = models.TextField(null=True)

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    class Meta:
        ordering = ['username']


class Base(models.Model):
    """Базовая модель для жанров и категорий."""
    name = models.CharField(max_length=40)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Category(Base):
    """Модель для категорий."""
    pass


class Genre(Base):
    """Модель для жанров."""
    pass


class Title(models.Model):
    """Модель для произведений."""
    name = models.CharField(
        'Произведение',
        max_length=200,
        help_text='Введите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(dt.date.today().year)],
        null=True,
        verbose_name='Год создания',
        help_text='Введите год создания произведения'
    )
    description = models.TextField(
        max_length=2000,
        verbose_name='Краткое описание произведения',
        help_text='Заполните краткое описание произведения',
        blank=True,
        null=True

    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        null=True,
        on_delete=models.SET_NULL
    )
    genre = models.ManyToManyField(
        Genre, related_name='genres', through='GenreTitle')

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель связи произведения и жанра."""
    title = models.ForeignKey(
        Title,
        null=True,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        null=True,
        on_delete=models.CASCADE
    )


class Review(models.Model):
    """Модель для рецензий."""
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст',
        blank=True
    )
    author = models.ForeignKey(
        User,
        related_name='reviews',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=10)
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text[:MAX_STR_LENGTH]

    class Meta:
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]


class Comment(models.Model):
    """Модель для комментариев."""
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text[:MAX_STR_LENGTH]

    class Meta:
        ordering = ['pub_date']
