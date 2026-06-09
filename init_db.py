"""
Скрипт инициализации БД и создания тестовых пользователей.
Запуск: python init_db.py
"""
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import Role, User, Genre, ReviewStatus

app = create_app()

with app.app_context():
    db.create_all()

    # Роли
    if not Role.query.first():
        roles = [
            Role(name='Администратор',
                 description='Суперпользователь — полный доступ, включая создание и удаление книг'),
            Role(name='Модератор',
                 description='Может редактировать книги и модерировать рецензии'),
            Role(name='Пользователь',
                 description='Может оставлять рецензии на книги'),
        ]
        db.session.add_all(roles)
        db.session.flush()

    # Статусы рецензий
    if not ReviewStatus.query.first():
        statuses = [
            ReviewStatus(name='На рассмотрении', description='Ожидает проверки модератором'),
            ReviewStatus(name='Одобрена', description='Опубликована'),
            ReviewStatus(name='Отклонена', description='Отклонена модератором'),
        ]
        db.session.add_all(statuses)

    # Жанры
    if not Genre.query.first():
        genre_names = [
            'Фантастика', 'Роман', 'Детектив', 'Классика',
            'Приключения', 'Ужасы', 'Биография', 'История', 'Научпоп', 'Поэзия'
        ]
        db.session.add_all([Genre(name=n) for n in genre_names])

    db.session.commit()

    # Тестовые пользователи
    if not User.query.first():
        admin_role = Role.query.filter_by(name='Администратор').first()
        mod_role = Role.query.filter_by(name='Модератор').first()
        user_role = Role.query.filter_by(name='Пользователь').first()

        users = [
            User(login='admin', password_hash=generate_password_hash('admin123'),
                 last_name='Администратов', first_name='Админ', middle_name='Админович',
                 role_id=admin_role.id),
            User(login='moderator', password_hash=generate_password_hash('mod123'),
                 last_name='Модераторов', first_name='Модер', middle_name=None,
                 role_id=mod_role.id),
            User(login='user', password_hash=generate_password_hash('user123'),
                 last_name='Пользователев', first_name='Пользователь', middle_name=None,
                 role_id=user_role.id),
        ]
        db.session.add_all(users)
        db.session.commit()
        print('✓ Тестовые пользователи созданы:')
        print('  admin / admin123 (Администратор)')
        print('  moderator / mod123 (Модератор)')
        print('  user / user123 (Пользователь)')
    else:
        print('✓ Пользователи уже существуют')

    print('✓ База данных инициализирована!')
