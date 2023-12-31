# API для YaMDb

- [Описание](#описание)
- [Функционал](#функционал)
  - [Модуль для загрузки CSV файлов](#модуль-для-загрузки-csv-файлов)
- [Технологии](#технологии)
- [Установка и запуск](#установка-и-запуск)
- [Документация к API](#документация-к-api)
  - [Алгоритм регистрации пользователей](#алгоритм-регистрации-пользователей)
  - [Пользовательские роли и права доступа](#пользовательские-роли-и-права-доступа)
- [Примеры запросов](#примеры-запросов)
- [Разработкчики](#разработчики)

# Описание
YaMDb собирает отзывы пользователей на произведения.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». 
Например, в категории «Книги» могут быть произведения 
«Винни-Пух и все-все-все» и «Марсианские хроники», а в категории 
«Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. 
Список категорий может быть расширен 
(например, можно добавить категорию «Изобразительное искусство» или 
«Ювелирка»). 

Произведению может быть присвоен жанр из списка предустановленных 
(например, «Сказка», «Рок» или «Артхаус»). 
Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые 
отзывы и ставят произведению оценку в диапазоне от одного до десяти 
(целое число); из пользовательских оценок формируется усреднённая оценка 
произведения — рейтинг (целое число). 
На одно произведение пользователь может оставить только один отзыв.
Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только 
аутентифицированные пользователи.

# Функционал 

- AUTH:
  - Регистрация нового пользователя.
  - Получение JWT-токена.
- CATEGORIES:
  - Получение списка всех категорий.
  - Добавление новой категории.
  - Удаление категории.
- GENRES:
  - Получение списка всех жанров.
  - Добавление жанра.
  - Удаление жанра.
- TITLES:
  - Получение списка всех произведений.
  - Добавление произведения.
  - Получение информации о произведении.
  - Частичное обновление информации о произведении.
  - Удаление произведения.
- REVIEWS:
  - Получение списка всех отзывов.
  - Добавление нового отзыва.
  - Полуение отзыва по id.
  - Частичное обновление отзыва по id.
  - Удаление отзыва по id.
- COMMENTS:
  - Получение списка всех комментариев к отзыву.
  - Добавление комментария к отзыву.
  - Получение комментария к отзыву.
  - Частичное обновление комментария к отзыву.
  - Удаление комментария к отзыву.
- USERS:
  - Получение списка всех пользователей.
  - Добавление пользователя.
  - Получение пользователя по username.
  - Изменение данных пользователя по username.
  - Удаление пользователя по username.
  - Получение данных своей учетной записи.
  - Изменение данных своей учетной записи.


### Модуль для загрузки CSV файлов
Позволяет осуществлять загрузку контента из `.CSV` файлов в базу данных.


# Технологии
- Python 3.9
- Django 3.2
- Django REST Framework 3.12.4
- SQLite3

# Установка и запуск

Клонировать репозиторий:
```bash
git clone <https or SSH URL>
```

Перейти в папку проекта:
```bash
cd api_yamdb
```

Создать и активировать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

Обновить pip:
```bash
python3 -m pip install --upgrade pip
```

Установить зависимости:
```bash
pip install -r requirements.txt
```

Выполнить миграции:
```bash
python3 api_yamdb/manage.py migrate
```
Заполнить базу данных контентом из csv файлов:
```bash
python3 api_yamdb/manage.py loadcsv
```
Запустить сервер:
```bash
python3 api_yamdb/manage.py runserver
```

# Документация к API
После запуска сервера, по адресу http://127.0.0.1:8000/redoc/ доступна документация к API.


### Алгоритм регистрации пользователей
Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами 
email и username на эндпоинт /api/v1/auth/signup/.
YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.
Пользователь отправляет POST-запрос с параметрами username и confirmation_code на 
эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).
При желании пользователь отправляет PATCH-запрос на эндпоинт /api/v1/users/me/ и 
заполняет поля в своём профайле (описание полей — в документации).

### Пользовательские роли и права доступа
**Аноним** — может просматривать описания произведений, читать отзывы и 
комментарии.

**Аутентифицированный пользователь (user)** — может читать всё, как и Аноним, 
может публиковать отзывы и ставить оценки произведениям 
(фильмам/книгам/песенкам), может комментировать отзывы; 
может редактировать и удалять свои отзывы и комментарии, редактировать свои 
оценки произведений. Эта роль присваивается по умолчанию каждому новому 
пользователю.

**Модератор (moderator)** — те же права, что и у Аутентифицированного 
пользователя, плюс право удалять и редактировать любые отзывы и комментарии.

**Администратор (admin)** — полные права на управление всем контентом проекта. 
Может создавать и удалять произведения, категории и жанры. 
Может назначать роли пользователям.

# Примеры запросов

`POST /api/v1/auth/signup/` - Регистрация пользователя
```json
{
  "email": "string",
  "username": "string"
}

```
`POST /api/v1/auth/token/` - Получить токен
```json
{
  "username": "string",
  "confirmation_code": "string"
}
```

***

`GET /api/v1/categories/` - Получить список всех категорий Права доступа: Доступно без токена

`POST /api/v1/categories/` - Создать категорию. Права доступа: Администратор. 
Поле slug каждой категории должно быть уникальным.
```json
{
"name": "string",
"slug": "string"
}
```

`DELETE /api/v1/categories/{slug}/` - Удалить категорию. Права доступа: Администратор.

***

`POST /api/v1/titles/{title_id}/reviews/` - Добавить новый отзыв. 
Пользователь может оставить только один отзыв на произведение. 
Права доступа: Аутентифицированные пользователи
```json
{
"text": "string",
"score": 1
}
```

`GET /api/v1/titles/{title_id}/reviews/{review_id}/` - Получить отзыв по id для указанного 
произведения. Права доступа: Доступно без токена.

`PATCH /api/v1/titles/{title_id}/reviews/{review_id}/` - Частично обновить отзыв по id. 
Права доступа: Автор отзыва, модератор или администратор.
```json
{
"text": "string",
"score": 1
}
```
# Разработчики
- [MrBoris6](https://github.com/MrBoris6) TeamLead/python backend developer
- [Sashka-Klu](https://github.com/Sashka-Klu) python backend developer
- [yapduser](https://github.com/yapduser) python backend developer
