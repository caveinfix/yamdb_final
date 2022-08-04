# Запуск: python manage.py import_csv

import csv
from django.core.management import BaseCommand

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment,
    GenreTitle,
    CustomUser,
)


MODELS = (
    Category,
    Title,
    Genre,
    GenreTitle,
    Comment,
)


class Command(BaseCommand):
    help = "Загрузка CSV файлов."

    def handle(self, *args, **options):
        if Title.objects.count() > 1:
            for model in MODELS:
                model.objects.all().delete()

        with open("static/data/users.csv", "r") as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                user_obj, created = CustomUser.objects.update_or_create(
                    id=row["id"],
                    username=row["username"],
                    email=row["email"],
                    role=row["role"]
                )

        with open("static/data/category.csv", "r") as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                category_obj, created = Category.objects.update_or_create(
                    id=row["id"],
                    name=row["name"],
                    slug=row["slug"],
                )

        with open(r"static/data/genre.csv", "r", encoding="utf-8") as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                genre_obj, created = Genre.objects.update_or_create(
                    id=row["id"], name=row["name"], slug=row["slug"]
                )

        with open(
            r"static/data/titles.csv", "r", encoding="utf-8"
        ) as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                category = Category.objects.get(id=row["category"])
                titles_obj, created = Title.objects.update_or_create(
                    id=row["id"],
                    name=row["name"],
                    year=row["year"],
                    category=category,
                )

        with open(
            r"static/data/genre_title.csv", "r", encoding="utf-8"
        ) as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                title = Title.objects.get(id=row["title_id"])
                genre = Genre.objects.get(id=row["genre_id"])
                genre_title_obj, created = GenreTitle.objects.update_or_create(
                    id=row["id"],
                    genre=genre,
                    title=title,
                )

        with open(
            r"static/data/review.csv", "r", encoding="utf-8"
        ) as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                title = Title.objects.get(id=row["title_id"])
                author = CustomUser.objects.get(pk=row["author"])
                review_obj, created = Review.objects.update_or_create(
                    id=row["id"],
                    title=title,
                    text=row["text"],
                    author=author,
                    score=row["score"],
                    pub_date=row["pub_date"],
                )

        with open(
            r"static/data/comments.csv", "r", encoding="utf-8"
        ) as csv_file:
            data = csv.DictReader(csv_file, delimiter=",")
            for row in data:
                review = Review.objects.get(id=row["review_id"])
                author = CustomUser.objects.get(id=row["author"])
                comment_obj, created = Comment.objects.update_or_create(
                    id=row["id"],
                    review=review,
                    text=row["text"],
                    author=author,
                    pub_date=row["pub_date"],
                )

        self.stdout.write(self.style.SUCCESS("Загрузка успешно завершена!"))
