![foodgram-project workflow](https://github.com/tetyorkin/foodgram-project/workflows/foodgram%20project/badge.svg)

# [Продуктовый помощник http://130.61.53.178/](http://130.61.53.178/)

Сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект разворачивается в трех Docker контейнерах припомощи Dokerfile и docker-compose.yaml

## Для раворачивания проекта требуются следующие действия:
- Склонировать данный репозиторий
- Создать файл `.env` и заполнить его своими данными
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
- Разворачиваем контейеры `sudo docker-compose up`
- Выполняем миграции, загружаем данные "Ингридиентов" в БД и собираем статику
```
sudo docker-compose -f docker-compose.yaml exec web python manage.py migrate --noinput && \
sudo docker-compose -f docker-compose.yaml exec web python manage.py load_data && \
sudo docker-compose -f docker-compose.yaml exec web python manage.py collectstatic
```


### Технологии
* [Python](https://www.python.org/) - высокоуровневый язык программирования общего назначения;
* [Django](https://www.djangoproject.com/) - фреймворк для веб-приложений;
* [Docker](https://www.docker.com/) - программное обеспечение для автоматизации развёртывания и управления приложениями в средах с поддержкой контейнеризации, контейнеризатор приложений.;
* 