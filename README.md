# Проект YaMDb

 [![Python application](https://github.com/hrapovd1/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)](https://github.com/hrapovd1/yamdb_final/actions/workflows/yamdb_workflow.yml)



### Описание
Проект YaMDb собирает отзывы (`Review`) пользователей на произведения (`Titles`). Произведения  
делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (`Category`) может  
быть расширен администратором. Сами произведения в YaMDb не хранятся, здесь нельзя  
посмотреть фильм или послушать музыку.
### Техническое описание
К проекту по адресу <http://localhost/redoc/> подключена документация API YaMDb.  
В ней описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса  
указаны уровни прав доступа: пользовательские роли, которым разрешён запрос.
### Пользовательские роли
- **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
- **Аутентифицированный пользователь** (`user`) — может читать всё, как и Аноним, может публиковать отзывы  
и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать  
и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по  
умолчанию каждому новому пользователю.
- **Модератор** (`moderator`) — те же права, что и у Аутентифицированного пользователя, плюс право удалять и  
редактировать любые отзывы и комментарии.
- **Администратор** (`admin`) — полные права на управление всем контентом проекта. Может создавать и удалять  
произведения, категории и жанры. Может назначать роли пользователям.
- **Суперюзер** Django должен всегда обладать правами администратора, пользователя с правами `admin`. Даже  
если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда  
администратор, но администратор — не обязательно суперюзер.
### Технологии
- [Python] v3.7
- [Django] v2.2.16
- [Django REST framework] v3.12.4
- [JWT] v5.2.0
### Запуск проекта
#### Минимальные требования к инфраструктуре:

- Docker Engine 20.10.0+
- docker compose 1.29.2

#### Установка переменных среды.
Для корректного запуска необходимо создать файл .env с переменными:
```BASH
cd infra
touch .env
```
Затем необходимо заполнить его следующими переменными:
```BASH
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Для запуска в продакшен среде необходимо создать отдельную базу для приложения, создать пользователя для этой базы и внести эти данные в .env файл.


#### Запуск
```BASH
cd infra
docker-compose up -d
``` 
- Настройка БД: 
```BASH
docker-compose exec web python3 manage.py migrate
```
- Создаем супер пользователя: 
```BASH
docker-compose exec web python3 manage.py createsuperuser
```
- Собираем статические файлы для корректного отображения страниц: 
```BASH
docker-compose exec web python3 manage.py collectstatic --noinput
```
- При желании можно импортировать тестовые данные из файлов csv, которые расположены в папке `api_yamdb/api_yamdb/static/data/`:
```BASH
docker-compose exec web python3 manage.py importcsv
```
    После этого необходимо еще раз добавить суперпользователя, т.к. ранее созданный сбивается после импорта тестовых данных.
### Авторы
- [Дмитрий Храпов]
- [Василий Глушков]
- [Александр Минаев]

[//]: # 
  [Python]: <https://www.python.org>
  [Django REST framework]: <https://www.django-rest-framework.org>
  [Django]: <https://www.djangoproject.com>
  [JWT]: <https://jwt.io>
  [Pillow]: <https://pillow.readthedocs.io/>
  [Дмитрий Храпов]: <https://github.com/hrapovd1>
  [Василий Глушков]: <https://github.com/Vasilii-byte>
  [Александр Минаев]: <https://github.com/AlexMinVrn>
