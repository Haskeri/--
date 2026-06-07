from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    @property
    def short_name(self):
        name = self.last_name
        if self.first_name:
            name += f' {self.first_name[0]}.'
        if self.middle_name:
            name += f' {self.middle_name[0]}.'
        return name

    def is_admin(self):
        return self.role.name == 'Администратор'

    def is_moderator(self):
        return self.role.name in ('Администратор', 'Модератор')

    def is_user(self):
        return self.role is not None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


book_genres = db.Table(
    'book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Cover(db.Model):
    __tablename__ = 'covers'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'))


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.Integer, db.ForeignKey('covers.id', ondelete='SET NULL'))
    cover = db.relationship('Cover', foreign_keys=[cover_id], uselist=False)
    genres = db.relationship('Genre', secondary=book_genres, lazy='subquery',
                             backref=db.backref('books', lazy=True))
    reviews = db.relationship('Review', backref='book', lazy='dynamic',
                              cascade='all, delete-orphan')

    @property
    def avg_rating(self):
        approved = self.reviews.filter_by(status_id=2).all()
        if not approved:
            return None
        return round(sum(r.rating for r in approved) / len(approved), 1)

    @property
    def review_count(self):
        return self.reviews.filter_by(status_id=2).count()


class ReviewStatus(db.Model):
    __tablename__ = 'review_statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reviews = db.relationship('Review', backref='status', lazy='dynamic')


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_id = db.Column(db.Integer, db.ForeignKey('review_statuses.id'), nullable=False, default=1)

    RATING_LABELS = {
        5: 'Отлично',
        4: 'Хорошо',
        3: 'Удовлетворительно',
        2: 'Неудовлетворительно',
        1: 'Плохо',
        0: 'Ужасно',
    }

    @property
    def rating_label(self):
        return self.RATING_LABELS.get(self.rating, str(self.rating))
