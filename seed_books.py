"""
Скрипт заполнения БД тестовыми книгами.
Запуск: python seed_books.py
"""
from app import create_app, db
from app.models import Book, Genre, Role, User, ReviewStatus
from werkzeug.security import generate_password_hash

app = create_app()

BOOKS = [
    {
        'title': 'Мастер и Маргарита',
        'author': 'Михаил Булгаков',
        'year': 1967,
        'publisher': 'YMCA-Press',
        'pages': 448,
        'genres': ['Роман', 'Классика'],
        'description': '''Один из величайших романов русской литературы XX века.

Дьявол в образе загадочного **Воланда** приезжает в советскую Москву со своей демонической свитой. Сатира на советское общество переплетается с историей Понтия Пилата и трагической любовной историей Мастера и Маргариты.

> «Трусость — это самый тяжкий порок» — одна из ключевых мыслей романа.''',
    },
    {
        'title': '1984',
        'author': 'Джордж Оруэлл',
        'year': 1949,
        'publisher': 'Secker & Warburg',
        'pages': 328,
        'genres': ['Фантастика', 'Классика'],
        'description': '''Культовая антиутопия о тоталитарном обществе будущего.

**Старший Брат** следит за каждым. Министерство Правды переписывает историю. Главный герой Уинстон Смит осмеливается думать иначе.

Одна из самых влиятельных книг XX века, подарившая миру понятия «двоемыслие», «мыслепреступление» и «комната 101».''',
    },
    {
        'title': 'Преступление и наказание',
        'author': 'Фёдор Достоевский',
        'year': 1866,
        'publisher': 'Русский вестник',
        'pages': 592,
        'genres': ['Роман', 'Классика'],
        'description': '''Психологический роман о студенте **Родионе Раскольникове**, решившемся на убийство ради проверки собственной теории о «право имеющих».

Глубокое исследование человеческой психологии, вины и искупления. Один из главных романов мировой литературы.''',
    },
    {
        'title': 'Гарри Поттер и философский камень',
        'author': 'Джоан Роулинг',
        'year': 1997,
        'publisher': 'Bloomsbury',
        'pages': 309,
        'genres': ['Фантастика', 'Приключения'],
        'description': '''Начало легендарной серии о мальчике-волшебнике.

**Гарри Поттер** узнаёт, что он волшебник, и поступает в школу чародейства и волшебства **Хогвартс**. Дружба, первые испытания и противостояние с тёмными силами.

Самая продаваемая книжная серия в истории — более 500 миллионов экземпляров.''',
    },
    {
        'title': 'Три товарища',
        'author': 'Эрих Мария Ремарк',
        'year': 1936,
        'publisher': 'Querido',
        'pages': 384,
        'genres': ['Роман', 'Классика'],
        'description': '''История о **дружбе** трёх молодых людей в послевоенной Германии.

Роберт, Готтфрид и Отто — три друга, объединённых фронтовым братством. На фоне политической нестабильности и экономического кризиса Роберт встречает **Патрицию Хольман**.

Один из самых трогательных романов о любви и потере.''',
    },
    {
        'title': 'Маленький принц',
        'author': 'Антуан де Сент-Экзюпери',
        'year': 1943,
        'publisher': 'Reynal & Hitchcock',
        'pages': 96,
        'genres': ['Классика', 'Приключения'],
        'description': '''Философская сказка для взрослых и детей.

Маленький принц путешествует с планеты на планету и встречает странных взрослых. На Земле он находит друга — лётчика — и учит его самому важному:

> «Зорко одно лишь сердце. Самого главного глазами не увидишь».''',
    },
    {
        'title': 'Шерлок Холмс. Этюд в багровых тонах',
        'author': 'Артур Конан Дойл',
        'year': 1887,
        'publisher': 'Ward Lock & Co',
        'pages': 224,
        'genres': ['Детектив', 'Классика'],
        'description': '''Первое появление легендарного **Шерлока Холмса** и его верного друга доктора Ватсона.

Двое мужчин найдены мёртвыми без видимых причин. Единственный след — слово *RACHE*, написанное кровью на стене. Холмс берётся за расследование.

Начало одной из величайших детективных серий в истории литературы.''',
    },
    {
        'title': 'Война и мир',
        'author': 'Лев Толстой',
        'year': 1869,
        'publisher': 'Русский вестник',
        'pages': 1274,
        'genres': ['Роман', 'История', 'Классика'],
        'description': '''Грандиозная эпопея о **войне 1812 года** и судьбах русских семей.

На фоне наполеоновского нашествия разворачиваются судьбы Болконских, Ростовых и Безуховых. Любовь, честь, смерть и поиск смысла жизни.

Один из самых известных романов в мировой литературе.''',
    },
]

with app.app_context():
    db.create_all()

    # Убеждаемся что жанры есть
    existing_genres = {g.name for g in Genre.query.all()}
    all_genre_names = set()
    for b in BOOKS:
        all_genre_names.update(b['genres'])

    for name in all_genre_names:
        if name not in existing_genres:
            db.session.add(Genre(name=name))
    db.session.commit()

    # Добавляем книги
    added = 0
    for data in BOOKS:
        if Book.query.filter_by(title=data['title']).first():
            print(f'  [пропуск] {data["title"]} — уже существует')
            continue

        genres = Genre.query.filter(Genre.name.in_(data['genres'])).all()
        book = Book(
            title=data['title'],
            author=data['author'],
            year=data['year'],
            publisher=data['publisher'],
            pages=data['pages'],
            description=data['description'],
            genres=genres,
        )
        db.session.add(book)
        added += 1

    db.session.commit()
    print(f'✓ Добавлено книг: {added}')

    # Создаём пользователей если нет
    if Role.query.first() and not User.query.filter_by(login='admin').first():
        admin_role = Role.query.filter_by(name='Администратор').first()
        mod_role   = Role.query.filter_by(name='Модератор').first()
        user_role  = Role.query.filter_by(name='Пользователь').first()
        h = generate_password_hash('admin123')
        db.session.add_all([
            User(login='admin',     password_hash=h, last_name='Ануфриев',    first_name='Платон', role_id=admin_role.id),
            User(login='moderator', password_hash=h, last_name='Модераторов', first_name='Модер',  role_id=mod_role.id),
            User(login='user',      password_hash=h, last_name='Читателев',   first_name='Читатель', role_id=user_role.id),
        ])
        db.session.commit()
        print('✓ Пользователи созданы (пароль: admin123)')

    print('✓ Готово!')
