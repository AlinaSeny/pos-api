CREATE TYPE order_status AS ENUM ('closed', 'opened');

CREATE TYPE payment_type AS ENUM ('cash', 'card');

CREATE TABLE orders(id SERIAL PRIMARY KEY, order_id UUID UNIQUE, status order_status, created_at TIMESTAMP, closed_at TIMESTAMP, payment_method payment_type, tips FLOAT);

CREATE TABLE menu(id SERIAL PRIMARY KEY, menu_id UUID UNIQUE, name VARCHAR(30) UNIQUE, price FLOAT, is_deleted BOOLEAN DEFAULT FALSE);

CREATE TABLE order_items(id SERIAL PRIMARY KEY, order_item_id UUID UNIQUE, order_id UUID REFERENCES orders(order_id), menu_id UUID REFERENCES menu(menu_id));

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO menu(menu_id, name, price) VALUES
(uuid_generate_v4(), 'Салат Цезарь', 350),
(uuid_generate_v4(), 'Стейк Рибай', 1200),
(uuid_generate_v4(), 'Паста Карбонара', 450),
(uuid_generate_v4(), 'Тирамису', 280),
(uuid_generate_v4(), 'Суп Том Ям', 390),
(uuid_generate_v4(), 'Пицца Маргарита', 550),
(uuid_generate_v4(), 'Бургер Чизбургер', 320),
(uuid_generate_v4(), 'Сок Апельсиновый', 150),
(uuid_generate_v4(), 'Кофе Латте', 180),
(uuid_generate_v4(), 'Чизкейк', 300);