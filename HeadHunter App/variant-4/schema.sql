-- Структура БД для HeadHunter mini (PostgreSQL)
-- Запуск:  psql -U postgres -d headhunter_db -f schema.sql

DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS vacancies CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL
);

CREATE TABLE vacancies (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR(100) NOT NULL,
    category            INTEGER NOT NULL,        -- 1 - IT, 2 - Продажи, 3 - Маркетинг
    salary              INTEGER NOT NULL,
    experience_required INTEGER NOT NULL,        -- опыт в годах
    description         TEXT NOT NULL,
    company_logo_path   VARCHAR(255) NOT NULL    -- /images/1.jpg ...
);

CREATE TABLE applications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vacancy_id  INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    apply_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cover_letter TEXT NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'  -- active | withdrawn
);

CREATE TABLE tokens (
    id         SERIAL PRIMARY KEY,
    key        VARCHAR(80) UNIQUE NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
