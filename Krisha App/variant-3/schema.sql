-- Структура БД для Krisha App (PostgreSQL)
-- Запуск:  psql -U postgres -d krisha_db -f schema.sql

DROP TABLE IF EXISTS favorites CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS ads CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

CREATE TABLE categories (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(200) NOT NULL,
    phone         VARCHAR(50) NOT NULL,
    avatar_path   VARCHAR(500)
);

CREATE TABLE ads (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    price       INTEGER NOT NULL CHECK (price > 0),
    rooms       INTEGER DEFAULT 0 CHECK (rooms >= 0),
    area        DECIMAL(10, 2) CHECK (area > 0),
    city        VARCHAR(100) NOT NULL,
    image_path  VARCHAR(500),
    status      VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'sold')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE favorites (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ad_id    INTEGER NOT NULL REFERENCES ads(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, ad_id)
);

CREATE TABLE tokens (
    id         SERIAL PRIMARY KEY,
    key        VARCHAR(80) UNIQUE NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
