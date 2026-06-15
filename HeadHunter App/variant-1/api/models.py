# Таблицы создаём сами через schema.sql, поэтому managed = False
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'users'


class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    category = models.IntegerField()
    salary = models.IntegerField()
    experience_required = models.IntegerField()
    description = models.TextField()
    company_logo_path = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'vacancies'


class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, db_column='vacancy_id')
    apply_date = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, default='active')

    class Meta:
        managed = False
        db_table = 'applications'


class Token(models.Model):
    key = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tokens'
