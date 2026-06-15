-- Структура БД для Cinema Ticket Booking App (PostgreSQL)
-- Запуск:  psql -U postgres -d cinema_db -f schema.sql

DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS movies CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    avatar_path   VARCHAR(255)
);

CREATE TABLE movies (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    genre        INTEGER NOT NULL,        -- 1 - action, 2 - comedy, 3 - drama
    ticket_price INTEGER NOT NULL,        -- цена за один билет
    age_rating   INTEGER NOT NULL,        -- 6, 12, 16, 18
    description  TEXT,
    poster_path  VARCHAR(255)
);

CREATE TABLE tickets (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    movie_id    INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    show_date   DATE NOT NULL,
    quantity    INTEGER NOT NULL CHECK (quantity >= 1),
    total_price INTEGER NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'  -- active | refunded
);

-- Таблица токенов авторизации (генерируемые токены, передаются как Bearer)
CREATE TABLE tokens (
    id         SERIAL PRIMARY KEY,
    key        VARCHAR(80) UNIQUE NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
