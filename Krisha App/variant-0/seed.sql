-- Начальные данные Krisha App (INSERT-only). Запуск после schema.sql:
--   psql -U postgres -d krisha_db -f seed.sql

INSERT INTO categories (name) VALUES
('Квартира'),
('Дом'),
('Офис'),
('Коммерческая недвижимость'),
('Земельный участок');


INSERT INTO users (username, password_hash, full_name, phone, avatar_path) VALUES
('seller_almaty', 'password123', 'Тимур Муратов', '+7 701 123 45 67', '/static/images/avatars/default-avatar-1.jpg'),
('astana_owner', 'password123', 'Айгуль Нуржанова', '+7 702 234 56 78', '/static/images/avatars/default-avatar-2.jpg'),
('shymkent_realtor', 'password123', 'Бауыржан Садыков', '+7 703 345 67 89', '/static/images/avatars/default-avatar-3.jpg');

INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(1, 1, '2-комнатная квартира в Медеуском районе', 
 'Светлая квартира в элитном жилом комплексе. Ремонт евро, мебель и техника остаются. Развитая инфраструктура, школа и садик рядом.', 
 45000000, 2, 68.5, 'Алматы', '/static/images/ads/1.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '5 days');

-- Объявление 2: Квартира в Астане (аренда)
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(2, 1, 'Сдам 1-комнатную квартиру в БЦ "Москва"', 
 'Уютная студия с современным ремонтом. Wi-Fi, кондиционер, подземный паркинг. Без комиссии. Для одного или пары.', 
 200000, 1, 42.0, 'Астана', '/static/images/ads/2.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '3 days');

-- Объявление 3: Дом в Алматы
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(1, 2, 'Продажа коттеджа в микрорайоне Таугуль', 
 '3-этажный дом с бассейном и сауной. Участок 12 соток. Свой газ, вода, центральная канализация. Отличное состояние.', 
 125000000, 5, 245.0, 'Алматы', '/static/images/ads/3.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '10 days');

-- Объявление 4: Офис в Шымкенте
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(3, 3, 'Офисное помещение в бизнес-центре "Шымкент Плаза"', 
 'Офис класса B. Отдельный вход, ресепшн, конференц-зал. Круглосуточная охрана, видеонаблюдение.', 
 25000000, 0, 85.0, 'Шымкент', '/static/images/ads/4.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '2 days');

-- Объявление 5: Квартира в Караганде
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(2, 1, '3-комнатная квартира в центре', 
 'Просторная квартира после капремонта. Пластиковые окна, натяжные потолки. Рядом парк, ТРЦ, остановки.', 
 28000000, 3, 82.0, 'Караганда', '/static/images/ads/5.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '7 days');

-- Объявление 6: Коммерческая недвижимость (Астана)
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(3, 4, 'Помещение свободного назначения на первом этаже', 
 'Отлично подходит под магазин, аптеку, стоматологию. Высокий трафик. Отдельный вход, все коммуникации.', 
 55000000, 0, 120.0, 'Астана', '/static/images/ads/6.jpg', 'sold', CURRENT_TIMESTAMP - INTERVAL '15 days');

-- Объявление 7: Земельный участок под ИЖС
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(1, 5, 'Участок 6 соток в элитном поселке', 
 'Документы готовы, электричество и газ на границе. Поселок охраняемый, центральный водопровод.', 
 18000000, 0, 6.0, 'Алматы', '/static/images/ads/7.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '20 days');

-- Объявление 8: Дом в Астане (аренда)
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(2, 2, 'Аренда таунхауса в районе Есиль', 
 'Современный таунхаус 120 м². Свой дворик, гараж на 2 машины. Мебель, техника, посуда. Для семьи.', 
 350000, 4, 120.0, 'Астана', '/static/images/ads/8.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '1 day');

-- Объявление 9: Квартира в Актау (продажа)
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(3, 1, '1-комнатная квартира с видом на море', 
 'Новостройка, сдача в этом году. Чистовая отделка. Закрытый двор, видеонаблюдение.', 
 22000000, 1, 45.0, 'Актау', '/static/images/ads/9.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '12 days');

-- Объявление 10: Офис в Алматы
INSERT INTO ads (user_id, category_id, title, description, price, rooms, area, city, image_path, status, created_at) VALUES
(1, 3, 'Аренда офиса в бизнес-центре "Нурлы Тау"', 
 'Престижный БЦ, панорамные окна. Отделка под ключ. Кофе-пойнт, переговорные. До метро 5 минут.', 
 450000, 0, 65.0, 'Алматы', '/static/images/ads/10.jpg', 'active', CURRENT_TIMESTAMP - INTERVAL '8 days');

-- =====================================================
-- 4. ИЗБРАННОЕ (для тестирования)
-- =====================================================
INSERT INTO favorites (user_id, ad_id, added_at) VALUES
(1, 2, CURRENT_TIMESTAMP - INTERVAL '1 day'),
(1, 4, CURRENT_TIMESTAMP - INTERVAL '2 days'),
(2, 1, CURRENT_TIMESTAMP - INTERVAL '3 days'),
(2, 8, CURRENT_TIMESTAMP - INTERVAL '1 day'),
(3, 5, CURRENT_TIMESTAMP - INTERVAL '5 days'),
(3, 9, CURRENT_TIMESTAMP - INTERVAL '4 days');

-- =====================================================
-- 5. ПРОВЕРОЧНЫЕ ЗАПРОСЫ (закомментированы)
-- =====================================================
-- SELECT COUNT(*) as total_users FROM users;
-- SELECT COUNT(*) as total_categories FROM categories;
-- SELECT COUNT(*) as total_ads FROM ads;
-- SELECT COUNT(*) as total_favorites FROM favorites;

-- Вывести сводку по объявлениям
-- SELECT 
--     a.id,
--     a.title,
--     a.price,
--     a.rooms,
--     a.area,
--     a.city,
--     c.name as category,
--     u.full_name as owner,
--     a.status,
--     a.created_at
-- FROM ads a
-- JOIN categories c ON a.category_id = c.id
-- JOIN users u ON a.user_id = u.id
-- ORDER BY a.created_at DESC;

-- Вывести избранное для каждого пользователя
-- SELECT 
--     u.username,
--     u.full_name,
--     a.title as ad_title,
--     a.price,
--     f.added_at
-- FROM favorites f
-- JOIN users u ON f.user_id = u.id
-- JOIN ads a ON f.ad_id = a.id
-- ORDER BY u.username, f.added_at DESC;

-- =====================================================
-- 6. ПРИМЕРЫ ЗАПРОСОВ ДЛЯ ФИЛЬТРАЦИИ
-- =====================================================

-- Фильтр по городу Алматы
-- SELECT * FROM ads WHERE city = 'Алматы' AND status = 'active';

-- Фильтр по цене (от 20 млн до 50 млн)
-- SELECT * FROM ads WHERE price BETWEEN 20000000 AND 50000000 AND status = 'active';

-- Фильтр по комнатам
-- SELECT * FROM ads WHERE rooms >= 2 AND status = 'active';

-- Сортировка по цене (возрастание)
-- SELECT * FROM ads WHERE status = 'active' ORDER BY price ASC;

-- Сортировка по дате (новые сверху)
-- SELECT * FROM ads WHERE status = 'active' ORDER BY created_at DESC;

-- Поиск по заголовку
-- SELECT * FROM ads WHERE title ILIKE '%квартира%' AND status = 'active';