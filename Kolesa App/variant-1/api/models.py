# Таблицы создаём сами через schema.sql, поэтому managed = False
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=50)
    avatar_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'users'


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    brand = models.CharField(max_length=80)
    model = models.CharField(max_length=80)
    year = models.IntegerField()
    price = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default='active')

    class Meta:
        managed = False
        db_table = 'ads'


class Token(models.Model):
    key = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tokens'
