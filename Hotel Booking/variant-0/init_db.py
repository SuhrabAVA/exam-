r"""
Создание базы данных и загрузка схемы (schema.sql) + данных (seed.sql) БЕЗ psql.
Работает через psycopg2, используя настройки из config/settings.py.

Запуск из папки проекта:
    venv\Scripts\python.exe init_db.py

ВНИМАНИЕ: скрипт пересоздаёт таблицы (schema.sql содержит DROP TABLE),
то есть все ранее введённые данные (зарегистрированные пользователи и т.п.)
будут стёрты и заменены на исходные данные из seed.sql.

Пароль/хост/порт берутся из переменных окружения DB_USER, DB_PASSWORD,
DB_HOST, DB_PORT (по умолчанию postgres / postgres / localhost / 5432).
"""
import os
import sys

# Корректный вывод кириллицы в консоль Windows независимо от кодовой страницы
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings  # noqa: E402

import psycopg2  # noqa: E402
from psycopg2 import sql  # noqa: E402

db = settings.DATABASES['default']
NAME = db['NAME']
conn_params = dict(
    host=db['HOST'],
    port=db['PORT'],
    user=db['USER'],
    password=db['PASSWORD'],
)


def run_sql_file(cursor, path):
    with open(path, 'r', encoding='utf-8') as f:
        cursor.execute(f.read())


def main():
    # 1) Создаём базу, если её ещё нет (подключаемся к служебной БД postgres)
    try:
        admin = psycopg2.connect(dbname='postgres', **conn_params)
    except (psycopg2.OperationalError, UnicodeDecodeError) as e:
        print('НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ К POSTGRESQL.')
        print(f'  host={conn_params["host"]} port={conn_params["port"]} user={conn_params["user"]}')
        print('  Вероятные причины:')
        print('   - неверный пароль пользователя postgres')
        print('     (задай $env:DB_PASSWORD = "пароль" или сбрось пароль')
        print('      скриптом reset-postgres-password.ps1);')
        print('   - PostgreSQL не запущен на этом порту.')
        print('  Подробности — в КАК-ЗАПУСТИТЬ.md.')
        sys.exit(1)

    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (NAME,))
        if cur.fetchone():
            print(f'База "{NAME}" уже существует — создание пропущено.')
        else:
            cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(NAME)))
            print(f'База "{NAME}" создана.')
    admin.close()

    # 2) Накатываем schema.sql, затем seed.sql
    conn = psycopg2.connect(dbname=NAME, **conn_params)
    conn.autocommit = True
    with conn.cursor() as cur:
        for fname in ('schema.sql', 'seed.sql'):
            if os.path.exists(fname):
                run_sql_file(cur, fname)
                print(f'{fname} выполнен.')
            else:
                print(f'ВНИМАНИЕ: файл {fname} не найден рядом с init_db.py.')
    conn.close()

    print('\nГотово! База готова к работе.')
    print('Запусти сервер:  venv\\Scripts\\python.exe manage.py runserver')
    print('Открой в браузере:  http://localhost:8000')


if __name__ == '__main__':
    main()
