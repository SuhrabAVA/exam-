# Таблицы создаём сами через schema.sql, поэтому managed = False
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'categories'


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    avatar_path = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'users'


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, db_column='category_id')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    rooms = models.IntegerField(default=0)
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=100)
    image_path = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'ads'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, db_column='ad_id')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'favorites'


class Token(models.Model):
    key = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tokens'
