-- АИС «Электронная библиотека»
-- Схема базы данных

CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_db;

-- Роли пользователей
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL
);

-- Пользователи
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Жанры
CREATE TABLE IF NOT EXISTS genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Обложки
CREATE TABLE IF NOT EXISTS covers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    md5_hash VARCHAR(32) NOT NULL,
    book_id INT
);

-- Книги
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    year YEAR NOT NULL,
    publisher VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    pages INT NOT NULL,
    cover_id INT,
    FOREIGN KEY (cover_id) REFERENCES covers(id) ON DELETE SET NULL
);

-- Добавляем внешний ключ в обложки (после создания книг)
ALTER TABLE covers ADD CONSTRAINT fk_covers_book
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE;

-- Связь книги-жанры (многие ко многим)
CREATE TABLE IF NOT EXISTS book_genres (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

-- Статусы рецензий (Вариант 1)
CREATE TABLE IF NOT EXISTS review_statuses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL
);

-- Рецензии
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 0 AND 5),
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_id INT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES review_statuses(id),
    UNIQUE KEY unique_user_book (user_id, book_id)
);

-- Начальные данные: роли
INSERT INTO roles (name, description) VALUES
    ('Администратор', 'Суперпользователь — имеет полный доступ к системе, включая создание и удаление книг'),
    ('Модератор', 'Может редактировать данные книг и производить модерацию рецензий'),
    ('Пользователь', 'Может оставлять рецензии на книги');

-- Начальные данные: статусы рецензий
INSERT INTO review_statuses (name, description) VALUES
    ('На рассмотрении', 'Рецензия ожидает проверки модератором'),
    ('Одобрена', 'Рецензия прошла проверку и опубликована'),
    ('Отклонена', 'Рецензия отклонена модератором');

-- Жанры
INSERT INTO genres (name) VALUES
    ('Фантастика'),
    ('Роман'),
    ('Детектив'),
    ('Классика'),
    ('Приключения'),
    ('Ужасы'),
    ('Биография'),
    ('История'),
    ('Научпоп'),
    ('Поэзия');

-- Тестовый администратор (пароль: admin123)
-- Хэш генерируется при первом запуске через create_admin.py
