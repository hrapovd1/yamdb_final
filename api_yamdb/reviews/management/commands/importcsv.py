import csv
from os.path import join

from django.core.management.base import BaseCommand
from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)

from api_yamdb.settings import STATIC_ROOT


class Command(BaseCommand):
    """Обработчик менеджмент-команды по импорту csv-данных в БД SQLite."""
    def handle(self, *args, **options):
        data_path = join(STATIC_ROOT, 'data')
        self.import_users(join(data_path, 'users.csv'))
        self.import_categories(join(data_path, 'category.csv'))
        self.import_genres(join(data_path, 'genre.csv'))
        self.import_titles(join(data_path, 'titles.csv'))
        self.import_genre_title(join(data_path, 'genre_title.csv'))
        self.import_review(join(data_path, 'review.csv'))
        self.import_comments(join(data_path, 'comments.csv'))

    def import_csv_file(self, conn, table_name, csv_file):
        cur = conn.cursor()
        header = ''
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.reader(read_file)
            for row in reader:
                if header == '':
                    header = ','.join(row)
                    col_count = len(row)
                    questions = ['?'] * col_count
                    questions_str = ','.join(questions)
                else:
                    insert_sql_str = (
                        f'INSERT INTO {table_name} ({header}) '
                        f'VALUES ({questions_str});'
                    )
                    self.stdout.write(insert_sql_str)
                    cur.execute(insert_sql_str, row)
        conn.commit()

    def import_users(self, csv_file):
        User.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )

    def import_categories(self, csv_file):
        Category.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

    def import_genres(self, csv_file):
        Genre.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

    def import_titles(self, csv_file):
        Title.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category']
                )

    def import_genre_title(self, csv_file):
        GenreTitle.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                GenreTitle.objects.get_or_create(
                    id=row['id'],
                    title_id=row['title_id'],
                    genre_id=row['genre_id']
                )

    def import_review(self, csv_file):
        Review.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                Review.objects.get_or_create(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                )

    def import_comments(self, csv_file):
        Comment.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            for row in reader:
                Comment.objects.get_or_create(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date']
                )
