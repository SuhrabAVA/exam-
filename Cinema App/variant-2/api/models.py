# Таблицы создаём сами через schema.sql, поэтому managed = False
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=150)
    avatar_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'users'


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.IntegerField()
    ticket_price = models.IntegerField()
    age_rating = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'movies'


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='movie_id')
    show_date = models.DateField()
    quantity = models.IntegerField()
    total_price = models.IntegerField()
    status = models.CharField(max_length=20, default='active')

    class Meta:
        managed = False
        db_table = 'tickets'


class Token(models.Model):
    key = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tokens'
