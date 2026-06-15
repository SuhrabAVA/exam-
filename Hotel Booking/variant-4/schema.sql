-- Структура БД для Hotel Booking App (PostgreSQL)
-- Запуск:  psql -U postgres -d hotel_db -f schema.sql

DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    avatar_path   VARCHAR(255)
);

CREATE TABLE rooms (
    id              SERIAL PRIMARY KEY,
    room_number     VARCHAR(20) NOT NULL,
    type            INTEGER NOT NULL,        -- 1 - standard, 2 - deluxe, 3 - suite
    price_per_night INTEGER NOT NULL,
    capacity        INTEGER NOT NULL,        -- вместимость человек
    description     TEXT,
    image_path      VARCHAR(255)
);

CREATE TABLE bookings (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id        INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    check_in_date  DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_price    INTEGER NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'active'  -- active | cancelled
);

CREATE TABLE tokens (
    id         SERIAL PRIMARY KEY,
    key        VARCHAR(80) UNIQUE NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
