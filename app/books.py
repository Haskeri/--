import hashlib
import os
import uuid

import bleach
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from app import db
from app.models import Book, Cover, Genre, Review

books_bp = Blueprint('books', __name__)

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'pre', 'code', 'blockquote', 'ul', 'ol', 'li', 'hr', 'img'
]
ALLOWED_ATTRS = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, 'img': ['src', 'alt']}


def sanitize(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)


@books_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = (Book.query
                  .order_by(Book.year.desc(), Book.id.desc())
                  .paginate(page=page, per_page=current_app.config['BOOKS_PER_PAGE'], error_out=False))
    return render_template('books/index.html', pagination=pagination, books=pagination.items)


@books_bp.route('/books/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    approved_reviews = (Review.query
                        .filter_by(book_id=book_id, status_id=2)
                        .order_by(Review.created_at.desc())
                        .all())
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            book_id=book_id, user_id=current_user.id
        ).first()
    return render_template('books/detail.html', book=book,
                           reviews=approved_reviews, user_review=user_review)


@books_bp.route('/books/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin():
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('books.index'))

    genres = Genre.query.order_by(Genre.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = sanitize(request.form.get('description', ''))
        year = request.form.get('year', type=int)
        publisher = request.form.get('publisher', '').strip()
        author = request.form.get('author', '').strip()
        pages = request.form.get('pages', type=int)
        genre_ids = request.form.getlist('genres', type=int)
        cover_file = request.files.get('cover')

        if not all([title, description, year, publisher, author, pages, genre_ids, cover_file]):
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/form.html', genres=genres, form_data=request.form)

        try:
            book = Book(
                title=title, description=description, year=year,
                publisher=publisher, author=author, pages=pages
            )
            selected_genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            book.genres = selected_genres
            db.session.add(book)
            db.session.flush()

            cover = _save_cover(cover_file, book.id)
            book.cover_id = cover.id
            db.session.commit()

            flash(f'Книга «{title}» успешно добавлена!', 'success')
            return redirect(url_for('books.detail', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('books/form.html', genres=genres, form_data={})


@books_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    if not current_user.is_moderator():
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('books.index'))

    book = Book.query.get_or_404(book_id)
    genres = Genre.query.order_by(Genre.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = sanitize(request.form.get('description', ''))
        year = request.form.get('year', type=int)
        publisher = request.form.get('publisher', '').strip()
        author = request.form.get('author', '').strip()
        pages = request.form.get('pages', type=int)
        genre_ids = request.form.getlist('genres', type=int)

        if not all([title, description, year, publisher, author, pages, genre_ids]):
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/form.html', book=book, genres=genres,
                                   form_data=request.form, editing=True)
        try:
            book.title = title
            book.description = description
            book.year = year
            book.publisher = publisher
            book.author = author
            book.pages = pages
            book.genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            db.session.commit()

            flash(f'Книга «{title}» успешно обновлена!', 'success')
            return redirect(url_for('books.detail', book_id=book.id))
        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('books/form.html', book=book, genres=genres,
                           form_data={}, editing=True)


@books_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
def delete(book_id):
    if not current_user.is_admin():
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('books.index'))

    book = Book.query.get_or_404(book_id)
    title = book.title

    cover_filename = None
    if book.cover:
        cover_filename = book.cover.filename

    try:
        db.session.delete(book)
        db.session.commit()

        if cover_filename:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], cover_filename)
            if os.path.exists(path):
                os.remove(path)

        flash(f'Книга «{title}» успешно удалена.', 'success')
    except Exception:
        db.session.rollback()
        flash('При удалении книги возникла ошибка.', 'danger')

    return redirect(url_for('books.index'))


def _save_cover(file, book_id):
    data = file.read()
    md5 = hashlib.md5(data).hexdigest()

    existing = Cover.query.filter_by(md5_hash=md5).first()
    if existing:
        return existing

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    filename = f'{uuid.uuid4().hex}.{ext}'

    cover = Cover(
        filename=filename,
        mime_type=file.mimetype,
        md5_hash=md5,
        book_id=book_id
    )
    db.session.add(cover)
    db.session.flush()

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'wb') as f:
        f.write(data)

    return cover
