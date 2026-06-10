from app import create_app, db
from app.models import Role, Genre, ReviewStatus

app = create_app()

with app.app_context():
    db.create_all()

    # Роли
    if not Role.query.first():
        db.session.add_all([
            Role(name='Администратор', description='Полный доступ к системе'),
            Role(name='Модератор', description='Редактирование книг и модерация рецензий'),
            Role(name='Пользователь', description='Оставляет рецензии'),
        ])
        db.session.commit()

    # Статусы рецензий
    if not ReviewStatus.query.first():
        db.session.add_all([
            ReviewStatus(name='На рассмотрении', description='Ожидает проверки'),
            ReviewStatus(name='Одобрена', description='Опубликована'),
            ReviewStatus(name='Отклонена', description='Отклонена модератором'),
        ])
        db.session.commit()

    # Жанры
    if not Genre.query.first():
        db.session.add_all([Genre(name=n) for n in [
            'Фантастика', 'Роман', 'Детектив', 'Классика',
            'Приключения', 'Ужасы', 'Биография', 'История', 'Научпоп', 'Поэзия'
        ]])
        db.session.commit()

app.run(debug=False, port=8090, host='0.0.0.0')
