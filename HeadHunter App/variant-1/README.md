# HeadHunter mini — поиск вакансий и отклики

Backend — Django (REST API, отдаёт JSON), frontend — статический
HTML/CSS/Vanilla JS, база данных — PostgreSQL.

## Требования

- Python 3.10+ (проверено на 3.14)
- PostgreSQL 14+ (установлен и запущен на порту **5432**)

## Запуск после `git clone`

```powershell
# 1) виртуальное окружение
python -m venv venv

# 2) зависимости
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# 3) если пароль пользователя postgres НЕ "postgres":
#    $env:DB_PASSWORD = "ваш_пароль"

# 4) создать базу headhunter_db и загрузить schema.sql + seed.sql (psql не нужен)
.\venv\Scripts\python.exe init_db.py

# 5) запустить сервер
.\venv\Scripts\python.exe manage.py runserver
```

Открыть в браузере: **http://localhost:8000**

## Важно

- **PostgreSQL должен быть установлен и запущен** на порту 5432. `git clone`
  скачивает только код — базу он не создаёт. Без PostgreSQL будет ошибка
  подключения.
- Параметры подключения — переменные окружения `DB_NAME`, `DB_USER`,
  `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (по умолчанию `headhunter_db` / postgres /
  postgres / localhost / 5432). См. `config/settings.py`.
- Чтобы войти, **зарегистрируй нового пользователя** на `register.html`.
- `init_db.py` пересоздаёт таблицы (в `schema.sql` есть DROP TABLE) — повторный
  запуск сбрасывает данные к исходным из `seed.sql`.

## Структура

- `api/` — модели, REST API (views), авторизация по токену
- `config/` — настройки Django и маршруты
- `frontend/` — HTML-страницы, `app.js`, `styles.css`
- `static/images/` — логотипы компаний из задания
- `schema.sql` — структура таблиц, `seed.sql` — начальные данные
- `init_db.py` — создание базы и загрузка schema + seed без psql
