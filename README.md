# CI и CD проекта api_yamdb
yamdb_final

![example workflow](https://github.com/caveinfix/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)


#  Workflow для проекта YaMDb

Проект YaMDb собирает отзывы пользователей на произведения. 
Произведения делятся на категории: «Книги», «Фильмы», «Музыка».

#  Настройки workflow

- автоматический запуск тестов,
- обновление образов на Docker Hub,
- автоматический деплой на боевой сервер при пуше в главную ветку main.
- уведомление в телеграмм 


## Документация и примеры
Посмотреть подробную документацию API:
```sh
http://51.250.18.244/redoc/
```
Пример вывода списка жанров:
```sh
http://51.250.18.244/api/v1/genres/
```

Автор проекта: Филипп https://github.com/caveinfix/