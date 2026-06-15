-- Начальные данные: 10 вакансий (логотипы /images/1.jpg ... /images/10.jpg)
-- Категории: 1 - IT, 2 - Продажи, 3 - Маркетинг
-- Запуск:  psql -U postgres -d headhunter_db -f seed.sql   (после schema.sql)

INSERT INTO vacancies (title, category, salary, experience_required, description, company_logo_path) VALUES
('Frontend Developer (Vue.js)', 1, 450000, 2, 'Разработка интерфейсов на Vue.js и TypeScript.', '/images/1.jpg'),
('Backend Engineer (Node.js)', 1, 550000, 3, 'Проектирование архитектуры серверной части на Express.', '/images/2.jpg'),
('Менеджер по продажам B2B', 2, 300000, 1, 'Активный поиск клиентов и проведение презентаций.', '/images/3.jpg'),
('SMM-специалист', 3, 200000, 0, 'Ведение социальных сетей и создание контента.', '/images/4.jpg'),
('Python Developer', 1, 600000, 4, 'Разработка сложных микросервисов на FastAPI.', '/images/5.jpg'),
('Руководитель отдела маркетинга', 3, 700000, 5, 'Стратегическое планирование и управление командой.', '/images/6.jpg'),
('Торговый представитель', 2, 250000, 0, 'Работа с розничными сетями в городе.', '/images/7.jpg'),
('Системный администратор', 1, 350000, 2, 'Поддержка IT-инфраструктуры офиса.', '/images/8.jpg'),
('Content Creator', 3, 180000, 1, 'Написание текстов и сценариев для видео.', '/images/9.jpg'),
('QA Automation Engineer', 1, 480000, 2, 'Автоматизация тестирования веб-приложений.', '/images/10.jpg');
