-- Структура БД для Kolesa App (PostgreSQL)
-- Запуск:  psql -U postgres -d kolesa_db -f schema.sql

DROP TABLE IF EXISTS ads CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    phone_number  VARCHAR(50) NOT NULL,
    avatar_path   VARCHAR(255)
);

CREATE TABLE ads (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    brand       VARCHAR(80) NOT NULL,
    model       VARCHAR(80) NOT NULL,
    year        INTEGER NOT NULL,
    price       INTEGER NOT NULL,
    description TEXT,
    image_path  VARCHAR(255),
    status      VARCHAR(20) NOT NULL DEFAULT 'active'  -- active | sold
);

CREATE TABLE tokens (
    id         SERIAL PRIMARY KEY,
    key        VARCHAR(80) UNIQUE NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
