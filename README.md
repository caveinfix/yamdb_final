# CI и CD проекта api_yamdb
![example workflow](https://github.com/caveinfix/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Проект YaMDb собирает отзывы пользователей на произведения. 
Произведения делятся на категории: «Книги», «Фильмы», «Музыка».

### Технологии
- Django 2.2.16
- Python 3.10.4
- Django REST Framework 3.12.4
- Simple-JWT 4.8.0
- PostgreSQL 13.0-alpine
- Nginx 1.21.3-alpine
- Gunicorn 20.0.4
- Docker 20.10.17
- Docker-compose 3.8

### Подоготовка к deploy на сервер
Необходимо сделать форк проекта и клонировать репозиторий локально для дальнейшей работы.

### Настройка секретов для actions
Устанавливаем значения для:
```
DB_ENGINE: django.db.backends.postgresql
DB_HOST: db
DB_NAME: postgres
DB_PORT: 5432
DOCKER_USERNAME: логин
DOCKER_PASSWORD: пароль
HOST: публичный IP сервера
USER: username сервера
PASSPHRASE: пароль для подключения к серверу по ssh(если установлен)
SSH_KEY: локальный ключ ssh
POSTGRES_PASSWORD: postgres
POSTGRES_USER: postgres
TELEGRAM_TO: токен пользователя (получить в userinfobot)
TELEGRAM_TOKEN: токен Вашего бота (получить в BotFather)
```
### Пример .env, который будет создан на сервере
```git
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password 
DB_HOST=db
DB_PORT=5432
```

### Копирование файлов на сервер
Переходим на локальной машине в папку infra и отправляем на сервер два файла:
- docker-compose.yaml

Пример:
```
scp docker-compose.yaml caveinfix@51.250.18.244:/home/caveinfix/
```
- далее переходим в папку infra/nginx и копируем default.conf предварительно изменив server_name <Ваш публичный IP>;

Пример:
```
scp default.conf caveinfix@51.250.18.244:/home/caveinfix/nginx/
```

### Установка docker-compose на сервер
Следующая команда загружает версию 1.26.0 и сохраняет исполняемый файл в каталоге /usr/local/bin/docker-compose, в результате чего данное программное обеспечение будет глобально доступно под именем docker-compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
Затем необходимо задать правильные разрешения, чтобы сделать команду docker-compose исполняемой:
```
sudo chmod +x /usr/local/bin/docker-compose
```
Чтобы проверить успешность установки, запустите следующую команду:
```
docker-compose --version
```

#  Для workflow настроены:

- автоматический запуск тестов,
- обновление образов на Docker Hub,
- автоматический деплой на боевой сервер при пуше в главную ветку main.
- уведомление в телеграмм 

Примеры команд, которые автоматически выполняются для сборки контейнера:
```
sudo docker-compose stop
sudo docker-compose rm web
touch .env
echo DB_ENGINE=${{ secrets.DB_ENGINE }} >> .env
echo DB_NAME=${{ secrets.DB_NAME }} >> .env
echo POSTGRES_USER=${{ secrets.POSTGRES_USER }} >> .env
echo POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }} >> .env
echo DB_HOST=${{ secrets.DB_HOST }} >> .env
echo DB_PORT=${{ secrets.DB_PORT }} >> .env
sudo docker-compose up -d
sudo docker-compose exec -T web python manage.py makemigrations
sudo docker-compose exec -T web python manage.py migrate
sudo docker-compose exec -T web python manage.py collectstatic --no-input
```

### Наполнение базы тестовыми данными
Дополнительно предусмотрен тестовый контент, который можно скопировать с локальной машины:

Переходим в папку infra, далее копируем на сервер командой:

Пример:
```
scp fixtures.json caveinfix@51.250.18.244:/home/caveinfix/
```
После копирования выполняем команду на сервер:
```
sudo docker-compose exec -T web python manage.py loaddata fixtures.json 
```

### Документация и примеры
Посмотреть подробную документацию API:
```sh
http://51.250.18.244/redoc/
```
Пример вывода списка жанров:
```sh
http://51.250.18.244/api/v1/genres/
```

Автор проекта: Филипп https://github.com/caveinfix/